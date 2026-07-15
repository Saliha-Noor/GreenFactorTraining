from fastapi import APIRouter, Depends
from database import get_db
from auth_utils import get_current_user

router = APIRouter()

@router.get("/billing/plan")
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

@router.get("/billing/subscription")
def get_billing_subscription(current_user: dict = Depends(get_current_user)):
    return get_billing_plan(current_user)

@router.get("/billing/usage")
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

@router.get("/analytics/usage")
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

@router.get("/analytics/history")
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
