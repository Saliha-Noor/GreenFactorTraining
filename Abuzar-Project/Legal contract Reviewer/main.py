"""FastAPI entry-point for the Multi-Agent Legal Contract Review System.

Endpoints:
  POST /api/upload              — upload a PDF contract, run the 4-agent pipeline
  GET  /api/reports             — list all past analysis reports
  GET  /api/reports/{id}        — retrieve a specific report
  GET  /api/reports/{id}/download — download the Word report
  GET  /api/clause-types        — list all 41 CUAD clause types
  GET  /                        — serve the frontend
"""

import sys
import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import UPLOAD_DIR, REPORTS_DIR, BASE_DIR
from database.connection import init_db, SessionLocal
from database.models import ClauseType, ClauseExample, AnalyzedContract
from agents.orchestrator import run_pipeline
from reports.docx_generator import generate_docx_report

# ── App setup ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Legal Contract Review System",
    description="Upload a PDF contract → get a structured risk analysis report powered by 4 AI agents and the CUAD dataset.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.on_event("startup")
def startup():
    init_db()
    UPLOAD_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


# ── Routes ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the main frontend page."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Frontend not found. Place index.html in /frontend/</h1>")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi import Response
    return Response(status_code=204)


# In-memory dictionary to track pipeline background tasks
active_tasks = {}


def run_pipeline_task(task_id: str, file_path: str, filename: str, timestamp: str):
    """Background worker to run the multi-agent review pipeline."""
    def status_callback(node_name: str, state: dict):
        # Map the completed node to the next agent that is now running
        next_agent_map = {
            "parser": "classifier",
            "classifier": "risk_analyzer",
            "risk_analyzer": "report_generator",
            "report_generator": "complete"
        }
        next_agent = next_agent_map.get(node_name, "parser")

        active_tasks[task_id] = {
            "status": "running",
            "current_agent": next_agent,
            "report": None,
            "errors": state.get("errors", []),
        }

    try:
        result = run_pipeline(file_path, status_callback=status_callback)
        final_report = result.get("final_report", {})
        status = result.get("status", "unknown")
        errors = result.get("errors", [])

        # Save report as Word document
        safe_name = filename.replace(" ", "_")
        report_path = REPORTS_DIR / f"{timestamp}_{safe_name.replace('.pdf', '_report.docx')}"
        try:
            generate_docx_report(final_report, report_path)
        except Exception as exc:
            print(f"[Warning] DOCX generation failed: {exc}")

        # Save to database
        db = SessionLocal()
        try:
            record = AnalyzedContract(
                filename=filename,
                page_count=final_report.get("page_count", 0),
                overall_risk_score=final_report.get("overall_risk_score", 0),
                parties=json.dumps(final_report.get("parties", [])),
                report_json=json.dumps(final_report, ensure_ascii=False),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            report_id = record.id
        finally:
            db.close()

        # Mark task as completed
        active_tasks[task_id] = {
            "status": "complete",
            "current_agent": None,
            "id": report_id,
            "report": final_report,
            "errors": errors,
        }

    except Exception as exc:
        print(f"[Error] Pipeline background task failed: {exc}")
        active_tasks[task_id] = {
            "status": "failed",
            "current_agent": None,
            "report": None,
            "errors": [str(exc)],
        }


@app.post("/api/upload")
async def upload_contract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a PDF contract and trigger the analysis pipeline in the background."""

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save uploaded file
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    save_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    print(f"\n[Upload] Saved: {save_path} ({len(content)} bytes)")

    # Generate a task ID
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "status": "running",
        "current_agent": "parser",
        "report": None,
        "errors": [],
    }

    # Queue the background pipeline execution
    background_tasks.add_task(
        run_pipeline_task,
        task_id,
        str(save_path),
        file.filename,
        timestamp
    )

    return JSONResponse(content={
        "task_id": task_id,
        "status": "queued"
    })


@app.get("/api/pipeline/status/{task_id}")
def get_pipeline_status(task_id: str):
    """Retrieve the real-time execution status of an active pipeline task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return active_tasks[task_id]


@app.get("/api/reports")
def list_reports():
    """List all previously analyzed contracts."""
    db = SessionLocal()
    try:
        records = db.query(AnalyzedContract).order_by(AnalyzedContract.upload_date.desc()).all()
        return [
            {
                "id": r.id,
                "filename": r.filename,
                "upload_date": r.upload_date.isoformat() if r.upload_date else None,
                "overall_risk_score": r.overall_risk_score,
                "page_count": r.page_count,
            }
            for r in records
        ]
    finally:
        db.close()


@app.get("/api/reports/{report_id}")
def get_report(report_id: int):
    """Retrieve a specific analysis report by ID."""
    db = SessionLocal()
    try:
        record = db.query(AnalyzedContract).filter(AnalyzedContract.id == report_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Report not found")
        return json.loads(record.report_json)
    finally:
        db.close()


@app.get("/api/reports/{report_id}/download")
def download_report(report_id: int):
    """Generate and download a Word (.docx) report for a specific analysis."""
    db = SessionLocal()
    try:
        record = db.query(AnalyzedContract).filter(AnalyzedContract.id == report_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Report not found")
        report_data = json.loads(record.report_json)
        safe_name = record.filename.replace(" ", "_").replace(".pdf", "")
        docx_path = REPORTS_DIR / f"{safe_name}_report_{report_id}.docx"
        generate_docx_report(report_data, docx_path)
        return FileResponse(
            path=str(docx_path),
            filename=f"{safe_name}_report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    finally:
        db.close()

@app.get("/api/clause-types")
def list_clause_types():
    """List all 41 CUAD clause types stored in the database."""
    db = SessionLocal()
    try:
        types = db.query(ClauseType).order_by(ClauseType.id).all()
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "risk_category": t.risk_category,
                "example_count": len(t.examples),
            }
            for t in types
        ]
    finally:
        db.close()


@app.get("/api/clause-examples/{clause_type_id}")
def get_clause_examples(clause_type_id: int, limit: int = 10):
    """Return CUAD example text spans for a specific clause type."""
    db = SessionLocal()
    try:
        ct = db.query(ClauseType).filter(ClauseType.id == clause_type_id).first()
        if not ct:
            raise HTTPException(status_code=404, detail="Clause type not found")
        examples = (
            db.query(ClauseExample)
            .filter(ClauseExample.clause_type_id == clause_type_id)
            .limit(limit)
            .all()
        )
        return {
            "clause_type": ct.name,
            "risk_category": ct.risk_category,
            "examples": [
                {
                    "id": ex.id,
                    "source_contract": ex.source_contract,
                    "text_span": ex.text_span[:500],
                }
                for ex in examples
            ],
        }
    finally:
        db.close()


@app.get("/api/stats")
def get_stats():
    """Return dashboard statistics."""
    db = SessionLocal()
    try:
        total_clause_types = db.query(ClauseType).count()
        total_examples = db.query(ClauseExample).count()
        total_contracts = db.query(AnalyzedContract).count()
        return {
            "total_clause_types": total_clause_types,
            "total_examples": total_examples,
            "total_contracts": total_contracts,
        }
    finally:
        db.close()


# ── Run with uvicorn ────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  MULTI-AGENT LEGAL CONTRACT REVIEW SYSTEM")
    print("  Starting server at http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
