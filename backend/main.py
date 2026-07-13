"""
GreenDev AI — FastAPI Backend
Orchestrates all agents and exposes REST endpoints for the React frontend.
"""

import os
import json
import asyncio
import hashlib
import hmac
import base64
import secrets
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from agents.code_analysis_agent  import analyze_code
from agents.energy_agent          import measure_energy
from agents.benchmark_agent       import get_benchmark, get_all_language_comparison
from agents.sci_agent             import get_sci_scores
from agents.planner_agent         import build_execution_plan, reflect_on_results
from agents.recommendation_agent  import get_recommendation
from report_generator             import generate_pdf, generate_markdown
from database import get_db, init_db
from notification_service import notification_service

load_dotenv()

app = FastAPI(title="GreenDev AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CARBON_INTENSITY_MAP = {
    "PK": 357.0,
    "EU": 230.0,
    "US": 370.0,
    "UK": 200.0,
    "AU": 620.0,
    "IN": 632.0,
    "CN": 536.0,
    "Global": 475.0,
}

JWT_SECRET = os.getenv("JWT_SECRET", "greendev-super-secret-key-12345!")

# ─── Auth Helper Functions ────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt_hex, key_hex = hashed.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload).encode('utf-8'))
    signature = hmac.new(
        JWT_SECRET.encode('utf-8'),
        f"{header_b64}.{payload_b64}".encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt(token: str) -> Optional[dict]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        expected_sig = hmac.new(
            JWT_SECRET.encode('utf-8'),
            f"{header_b64}.{payload_b64}".encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64url_encode(expected_sig)
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
        return json.loads(base64url_decode(payload_b64).decode('utf-8'))
    except Exception:
        return None

# ─── Auth Verification Dependency ──────────────────────────────────────────────

def get_current_user(authorization: str = Header(None), x_api_key: str = Header(None)):
    db = next(get_db())
    try:
        # 1. JWT Check
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = verify_jwt(token)
            if payload and "user_id" in payload:
                cursor = db.cursor()
                cursor.execute("SELECT id, email, name, organization FROM users WHERE id = ?", (payload["user_id"],))
                user = cursor.fetchone()
                if user:
                    return dict(user)

        # 2. API Key Check
        if x_api_key:
            cursor = db.cursor()
            cursor.execute("SELECT user_id, id, key_string FROM api_keys WHERE key_string = ? AND is_active = 1", (x_api_key,))
            key_row = cursor.fetchone()
            if key_row:
                # Update usage stats
                cursor.execute(
                    "UPDATE api_keys SET usage_count = usage_count + 1, last_used_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), key_row["id"])
                )
                db.commit()
                # Get User
                cursor.execute("SELECT id, email, name, organization FROM users WHERE id = ?", (key_row["user_id"],))
                user = cursor.fetchone()
                if user:
                    return dict(user)

        raise HTTPException(status_code=401, detail="Authentication failed. Log in or provide a valid API Key.")
    finally:
        db.close()

# ─── Pydantic Schemas ──────────────────────────────────────────────────────────

class RegisterSchema(BaseModel):
    email: str
    password: str
    name: Optional[str] = ""
    organization: Optional[str] = ""

class LoginSchema(BaseModel):
    email: str
    password: str

class ProfileUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    organization: Optional[str] = None

class PreferencesSchema(BaseModel):
    carbon_region: Optional[str] = None
    report_format: Optional[str] = None
    notify_analysis: Optional[int] = None
    notify_weekly: Optional[int] = None
    notify_security: Optional[int] = None
    notify_updates: Optional[int] = None
    notify_marketing: Optional[int] = None
    notify_alerts: Optional[int] = None

class ApiKeyGenerateSchema(BaseModel):
    name: Optional[str] = "Default Key"

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# 1. Registration / Login
@app.post("/auth/register")
def register(data: RegisterSchema):
    db = next(get_db())
    cursor = db.cursor()
    try:
        # Check uniqueness
        cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already registered.")

        # Create user
        p_hash = hash_password(data.password)
        cursor.execute(
            "INSERT INTO users (email, name, organization, password_hash) VALUES (?, ?, ?, ?)",
            (data.email, data.name, data.organization, p_hash)
        )
        user_id = cursor.lastrowid

        # Setup preferences defaults
        cursor.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
        
        # Setup subscription defaults
        cursor.execute("INSERT INTO subscriptions (user_id) VALUES (?)", (user_id,))

        # Setup analytics defaults
        cursor.execute("INSERT INTO analytics (user_id) VALUES (?)", (user_id,))

        # Generate a default API Key
        default_key = f"sk_greendev_{secrets.token_hex(20)}"
        cursor.execute(
            "INSERT INTO api_keys (user_id, key_string, name) VALUES (?, ?, ?)",
            (user_id, default_key, "Initial API Key")
        )

        db.commit()

        # Create token
        token = create_jwt({"user_id": user_id, "email": data.email})
        return {
            "token": token,
            "user": {"id": user_id, "email": data.email, "name": data.name, "organization": data.organization}
        }
    finally:
        db.close()

@app.post("/auth/login")
def login(data: LoginSchema):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, email, name, organization, password_hash FROM users WHERE email = ?", (data.email,))
        user = cursor.fetchone()
        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        token = create_jwt({"user_id": user["id"], "email": user["email"]})
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "organization": user["organization"]
            }
        }
    finally:
        db.close()

# 2. Profile Management
@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@app.put("/profile")
def update_profile(data: ProfileUpdateSchema, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        # Check email uniqueness if modified
        if data.email and data.email != current_user["email"]:
            cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already taken.")

        new_email = data.email if data.email else current_user["email"]
        new_name = data.name if data.name is not None else current_user["name"]
        new_org = data.organization if data.organization is not None else current_user["organization"]

        cursor.execute(
            "UPDATE users SET email = ?, name = ?, organization = ? WHERE id = ?",
            (new_email, new_name, new_org, current_user["id"])
        )
        db.commit()
        return {"id": current_user["id"], "email": new_email, "name": new_name, "organization": new_org}
    finally:
        db.close()

# 3. Delete Account
@app.delete("/account")
def delete_account(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        # Cascade will delete keys, preferences, history, analytics, subscriptions
        cursor.execute("DELETE FROM users WHERE id = ?", (current_user["id"],))
        db.commit()
        return {"status": "success", "message": "Account successfully deleted."}
    finally:
        db.close()

# 4. API Billing / Plan System
@app.get("/billing/plan")
def get_billing_plan(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT plan_type, limits, status, expiration FROM subscriptions WHERE user_id = ?", (current_user["id"],))
        row = cursor.fetchone()
        if not row:
            return {"plan_type": "Local Plan", "limits": -1, "status": "Active", "expiration": None}
        return dict(row)
    finally:
        db.close()

@app.get("/billing/subscription")
def get_billing_subscription(current_user: dict = Depends(get_current_user)):
    return get_billing_plan(current_user)

@app.get("/billing/usage")
def get_billing_usage(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT total_requests FROM analytics WHERE user_id = ?", (current_user["id"],))
        row = cursor.fetchone()
        requests = row["total_requests"] if row else 0
        return {"requests_used": requests, "quota": -1, "billing_period": "Unlimited"}
    finally:
        db.close()

# 5. API Usage Analytics
@app.get("/analytics/usage")
def get_analytics_usage(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT total_requests, daily_requests, monthly_requests, last_request_timestamp,
                   total_analyses, successful_analyses, failed_analyses, total_processing_time
            FROM analytics WHERE user_id = ?
        """, (current_user["id"],))
        row = cursor.fetchone()
        if not row:
            return {
                "total_requests": 0, "daily_requests": 0, "monthly_requests": 0,
                "last_request_timestamp": None, "total_analyses": 0, "successful_analyses": 0,
                "failed_analyses": 0, "average_processing_time": 0.0
            }
        
        data = dict(row)
        # Avoid zero division
        successes = data["successful_analyses"]
        total_time = data["total_processing_time"]
        data["average_processing_time"] = round(total_time / successes, 3) if successes > 0 else 0.0
        return data
    finally:
        db.close()

@app.get("/analytics/history")
def get_analytics_history(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id, filename, score, co2_grams, savings_kg, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC",
            (current_user["id"],)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

# 6. Real API Key Management
@app.get("/api-keys")
def list_api_keys(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, key_string, name, created_at, last_used_at, usage_count, is_active FROM api_keys WHERE user_id = ?", (current_user["id"],))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

@app.post("/api-keys")
def generate_api_key(data: ApiKeyGenerateSchema, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        new_key = f"sk_greendev_{secrets.token_hex(20)}"
        cursor.execute(
            "INSERT INTO api_keys (user_id, key_string, name) VALUES (?, ?, ?)",
            (current_user["id"], new_key, data.name)
        )
        db.commit()
        return {"status": "success", "key": {"id": cursor.lastrowid, "key_string": new_key, "name": data.name, "created_at": datetime.now().isoformat()}}
    finally:
        db.close()

@app.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: int, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        # Check ownership
        cursor.execute("SELECT id FROM api_keys WHERE id = ? AND user_id = ?", (key_id, current_user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="API Key not found or does not belong to you.")
        cursor.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
        db.commit()
        return {"status": "success", "message": "API key revoked successfully."}
    finally:
        db.close()

# 7. Notification Preferences
@app.get("/preferences")
def get_preferences(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT carbon_region, report_format, notify_analysis, notify_weekly,
                   notify_security, notify_updates, notify_marketing, notify_alerts
            FROM user_preferences WHERE user_id = ?
        """, (current_user["id"],))
        row = cursor.fetchone()
        if not row:
            return {"carbon_region": "Global", "report_format": "PDF"}
        return dict(row)
    finally:
        db.close()

@app.put("/preferences")
def update_preferences(data: PreferencesSchema, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        # Build dynamic query update values
        fields = []
        params = []
        for key, val in data.dict(exclude_none=True).items():
            fields.append(f"{key} = ?")
            params.append(val)
        
        if not fields:
            return get_preferences(current_user)

        params.append(current_user["id"])
        query = f"UPDATE user_preferences SET {', '.join(fields)} WHERE user_id = ?"
        cursor.execute(query, params)
        db.commit()
        return get_preferences(current_user)
    finally:
        db.close()

# 8. Trajectory Projections API
@app.get("/analysis/{analysis_id}/projection")
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

# 9. Static CMS content: Help & FAQ
@app.get("/help")
def get_help_articles():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_index, category_name, heading, body FROM help_articles ORDER BY category_index, display_order")
        rows = cursor.fetchall()
        
        # Group by category_index
        grouped = {}
        for r in rows:
            idx = r["category_index"]
            if idx not in grouped:
                grouped[idx] = {
                    "title": r["category_name"],
                    "sections": []
                }
            grouped[idx]["sections"].append({
                "heading": r["heading"],
                "body": r["body"]
            })
        return grouped
    finally:
        db.close()

@app.get("/faq")
def get_faq_list():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_index, question, answer FROM faqs ORDER BY category_index, display_order")
        rows = cursor.fetchall()
        
        grouped = {}
        for r in rows:
            idx = r["category_index"]
            if idx not in grouped:
                grouped[idx] = []
            grouped[idx].append({
                "q": r["question"],
                "a": r["answer"]
            })
        return grouped
    finally:
        db.close()

# 10. Static CMS Content: Tutorials
@app.get("/tutorials")
def get_tutorials():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_index, title, duration, url, thumbnail FROM video_tutorials ORDER BY category_index, display_order")
        rows = cursor.fetchall()
        
        grouped = {}
        for r in rows:
            idx = r["category_index"]
            if idx not in grouped:
                grouped[idx] = []
            grouped[idx].append({
                "title": r["title"],
                "duration": r["duration"],
                "url": r["url"],
                "thumbnail": r["thumbnail"]
            })
        return grouped
    finally:
        db.close()

# 11. Static CMS Content: Language benchmarks
@app.get("/benchmarks/languages")
def get_benchmark_notes():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT language, factor, energy_notes, runtime_notes, rapl_notes FROM benchmark_notes ORDER BY display_order")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

# 12. Sample Scripts
@app.get("/samples")
def get_sample_scripts():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT filename, score, verdict, color, source_code FROM sample_scripts ORDER BY display_order")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

# 13. CORE Analysis Endpoint with JWT/API Key validation & Auto logging
@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    carbon_region: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    start_time = datetime.now()
    raw_bytes   = await file.read()
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


@app.post("/report/pdf")
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

        os.makedirs("reports", exist_ok=True)
        path = generate_pdf(code_stats, energy_data, benchmark_data, sci_scores,
                            recommendation, reflection)

        return FileResponse(path, media_type="application/pdf",
                            filename="greendev_report.pdf")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/report/markdown")
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

        os.makedirs("reports", exist_ok=True)
        path = f"reports/greendev_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return FileResponse(path, media_type="text/markdown", filename="greendev_report.md")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Markdown generation failed: {str(e)}")

# Initialize DB on start
init_db()
