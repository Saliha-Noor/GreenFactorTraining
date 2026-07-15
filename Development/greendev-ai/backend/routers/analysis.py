import os
import json
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from database import get_db
from auth_utils import get_current_user, CARBON_INTENSITY_MAP
from agents.code_analysis_agent  import analyze_code
from agents.energy_agent          import measure_energy
from agents.benchmark_agent       import get_benchmark, get_all_language_comparison
from agents.sci_agent             import get_sci_scores
from agents.planner_agent         import build_execution_plan, reflect_on_results
from agents.recommendation_agent  import get_recommendation
from report_generator             import generate_pdf, generate_markdown, REPORTS_DIR
from notification_service import notification_service

router = APIRouter()

@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    carbon_region: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    start_time = datetime.now()
    raw_bytes   = await file.read()
    if len(raw_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds the 5 MB limit.")
    code_string = raw_bytes.decode("utf-8")

    if not code_string.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    db = next(get_db())
    cursor = db.cursor()
    try:
        # Load user region if not explicitly provided in the form
        if not carbon_region:
            cursor.execute("SELECT carbon_region FROM user_preferences WHERE user_id = ?", (current_user["id"],))
            row = cursor.fetchone()
            carbon_region = row["carbon_region"] if row else "Global"

        # ── Agent 1: Code Analysis ──────────────────────────────────────────────
        code_stats = analyze_code(code_string)
        if "error" in code_stats:
            cursor.execute(
                "UPDATE analytics SET failed_analyses = failed_analyses + 1, total_requests = total_requests + 1 WHERE user_id = ?",
                (current_user["id"],)
            )
            db.commit()
            raise HTTPException(status_code=422, detail=code_stats["error"])

        # ── Planner: Build execution plan ───────────────────────────────────────
        plan = build_execution_plan(code_stats)

        # ── Agent 2 + 3 (parallel) ──────────────────────────────────────────────
        loop = asyncio.get_event_loop()
        energy_task    = loop.run_in_executor(None, measure_energy, code_string)
        benchmark_task = loop.run_in_executor(None, get_benchmark, code_stats["task_type"])

        energy_data, benchmark_data = await asyncio.gather(energy_task, benchmark_task)

        # Language comparison list
        lang_comparison = get_all_language_comparison(code_stats["task_type"])

        # ── Agent 4: SCI ────────────────────────────────────────────────────────
        carbon_intensity = CARBON_INTENSITY_MAP.get(carbon_region, 475.0)
        sci_scores = get_sci_scores(energy_data, benchmark_data, carbon_intensity=carbon_intensity)

        # ── Planner: Reflect on results ──────────────────────────────────────────
        reflection = reflect_on_results(code_stats, energy_data, benchmark_data, sci_scores)

        # ── Agent 5: Recommendation ─────────────────────────────────────────────
        recommendation = get_recommendation(
            code_stats, energy_data, benchmark_data, sci_scores, reflection, code_string
        )

        res_payload = {
            "filename":         file.filename,
            "code_stats":       code_stats,
            "energy_data":      energy_data,
            "benchmark_data":   benchmark_data,
            "lang_comparison":  lang_comparison,
            "sci_scores":       sci_scores,
            "recommendation":   recommendation,
            "planner": {
                "plan":       plan,
                "reflection": reflection,
            },
            "timestamp": datetime.now().isoformat(),
        }

        # ─── LOGGING & METRICS UPDATES ──────────────────────────────────────────
        duration = (datetime.now() - start_time).total_seconds()
        
        score_val = sci_scores["estimated_sci"]
        co2_grams = energy_data["co2_grams"]
        
        yearly_current = recommendation.get("carbon_projection", {}).get("yearly_co2_kg", 0.0)
        yearly_opt = recommendation.get("carbon_projection", {}).get("yearly_co2_kg_optimized", 0.0)
        savings_val = max(0.0, yearly_current - yearly_opt)

        # Insert run history with result payload cache
        cursor.execute(
            """
            INSERT INTO history (user_id, filename, score, co2_grams, savings_kg, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (current_user["id"], file.filename, score_val, co2_grams, savings_val, json.dumps(res_payload))
        )
        history_id = cursor.lastrowid

        # Update analytical stats
        cursor.execute(
            """
            UPDATE analytics
            SET total_requests = total_requests + 1,
                total_analyses = total_analyses + 1,
                successful_analyses = successful_analyses + 1,
                total_processing_time = total_processing_time + ?,
                last_request_timestamp = ?
            WHERE user_id = ?
            """,
            (duration, datetime.now().isoformat(), current_user["id"])
        )
        db.commit()

        # Add analysis ID to response payload
        res_payload["analysis_id"] = history_id

        # Pluggable Email Notifications Trigger
        cursor.execute("SELECT notify_analysis FROM user_preferences WHERE user_id = ?", (current_user["id"],))
        pref = cursor.fetchone()
        if pref and pref["notify_analysis"]:
            notification_service.send_analysis_complete_email(
                current_user["email"],
                file.filename,
                recommendation.get("green_score", {}).get("overall", 0.0) / 10.0,
                sci_scores["estimated_sci"]
            )

        return res_payload
    except Exception as e:
        import traceback
        traceback.print_exc()
        cursor.execute(
            "UPDATE analytics SET failed_analyses = failed_analyses + 1, total_requests = total_requests + 1 WHERE user_id = ?",
            (current_user["id"],)
        )
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/analysis/{analysis_id}/projection")
def get_analysis_projection(analysis_id: int, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT result_json FROM history WHERE id = ? AND user_id = ?", (analysis_id, current_user["id"]))
        row = cursor.fetchone()
        if not row or not row["result_json"]:
            raise HTTPException(status_code=404, detail="Analysis history record not found.")

        result = json.loads(row["result_json"])
        carbon_proj = result.get("recommendation", {}).get("carbon_projection", {})
        
        current_yr = carbon_proj.get("yearly_co2_kg", 0.0)
        optimized_yr = carbon_proj.get("yearly_co2_kg_optimized", 0.0)
        savings = max(0.0, current_yr - optimized_yr)
        
        # Build 12-month projections
        monthly_labels = [f"Month {i}" for i in range(1, 13)]
        current_emissions = [round(max(0.0, current_yr - i * (current_yr * 0.015)), 2) for i in range(12)]
        optimized_emissions = [round(max(0.0, optimized_yr - i * (optimized_yr * 0.015)), 2) for i in range(12)]
        
        return {
            "monthly_labels": monthly_labels,
            "current_emissions": current_emissions,
            "optimized_emissions": optimized_emissions,
            "percentage_reduction": carbon_proj.get("savings_percent", 0.0),
            "cumulative_savings": round(savings, 2)
        }
    finally:
        db.close()


@router.get("/report/{analysis_id}/download")
def download_existing_report(analysis_id: int, format: str = "pdf", current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT result_json FROM history WHERE id = ? AND user_id = ?", (analysis_id, current_user["id"]))
        row = cursor.fetchone()
        if not row or not row["result_json"]:
            raise HTTPException(status_code=404, detail="Analysis record not found.")

        result = json.loads(row["result_json"])
        
        code_stats = result.get("code_stats", {})
        energy_data = result.get("energy_data", {})
        benchmark_data = result.get("benchmark_data", {})
        sci_scores = result.get("sci_scores", {})
        recommendation = result.get("recommendation", {})
        planner = result.get("planner", {})
        reflection = planner.get("reflection", {}) if planner else {}

        os.makedirs(REPORTS_DIR, exist_ok=True)
        if format.lower() == "pdf":
            path = generate_pdf(code_stats, energy_data, benchmark_data, sci_scores,
                                recommendation, reflection)
            return FileResponse(path, media_type="application/pdf",
                                filename=f"greendev_report_{analysis_id}.pdf")
        else:
            md_content = generate_markdown(code_stats, energy_data, benchmark_data,
                                           sci_scores, recommendation, planner.get("plan"), reflection)
            path = os.path.join(REPORTS_DIR, f"greendev_report_{analysis_id}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(md_content)
            return FileResponse(path, media_type="text/markdown",
                                filename=f"greendev_report_{analysis_id}.md")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Report download failed: {str(e)}")
    finally:
        db.close()


@router.post("/report/pdf")
async def download_pdf(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        raw_bytes   = await file.read()
        code_string = raw_bytes.decode("utf-8")

        code_stats     = analyze_code(code_string)
        energy_data    = measure_energy(code_string)
        benchmark_data = get_benchmark(code_stats.get("task_type", "general"))
        sci_scores     = get_sci_scores(energy_data, benchmark_data)
        reflection     = reflect_on_results(code_stats, energy_data, benchmark_data, sci_scores)
        recommendation = get_recommendation(code_stats, energy_data, benchmark_data, sci_scores, reflection, code_string)

        path = generate_pdf(code_stats, energy_data, benchmark_data, sci_scores,
                            recommendation, reflection)

        return FileResponse(path, media_type="application/pdf",
                            filename="greendev_report.pdf")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/report/markdown")
async def download_markdown(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        raw_bytes   = await file.read()
        code_string = raw_bytes.decode("utf-8")

        code_stats     = analyze_code(code_string)
        energy_data    = measure_energy(code_string)
        benchmark_data = get_benchmark(code_stats.get("task_type", "general"))
        sci_scores     = get_sci_scores(energy_data, benchmark_data)
        reflection     = reflect_on_results(code_stats, energy_data, benchmark_data, sci_scores)
        recommendation = get_recommendation(code_stats, energy_data, benchmark_data, sci_scores, reflection, code_string)

        md_content = generate_markdown(code_stats, energy_data, benchmark_data,
                                       sci_scores, recommendation, None, reflection)

        os.makedirs(REPORTS_DIR, exist_ok=True)
        path = os.path.join(REPORTS_DIR, f"greendev_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return FileResponse(path, media_type="text/markdown", filename="greendev_report.md")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Markdown generation failed: {str(e)}")
