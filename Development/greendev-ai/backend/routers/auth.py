from fastapi import APIRouter, Depends, HTTPException
import secrets
from datetime import datetime
from database import get_db
from auth_utils import (
    RegisterSchema, LoginSchema, ProfileUpdateSchema, PreferencesSchema, ApiKeyGenerateSchema,
    hash_password, verify_password, create_jwt, get_current_user
)

router = APIRouter()

@router.post("/auth/register")
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

@router.post("/auth/login")
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

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/profile")
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

@router.delete("/account")
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

@router.get("/api-keys")
def list_api_keys(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, key_string, name, created_at, last_used_at, usage_count, is_active FROM api_keys WHERE user_id = ?", (current_user["id"],))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

@router.post("/api-keys")
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

@router.delete("/api-keys/{key_id}")
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

@router.get("/preferences")
def get_preferences(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT carbon_region, report_format, notify_analysis,
                   notify_updates, notify_marketing, notify_alerts
            FROM user_preferences WHERE user_id = ?
        """, (current_user["id"],))
        row = cursor.fetchone()
        if not row:
            return {"carbon_region": "Global", "report_format": "PDF", "notify_weekly": 0, "notify_security": 1}
        res = dict(row)
        res["notify_weekly"] = 0
        res["notify_security"] = 1
        return res
    finally:
        db.close()

@router.put("/preferences")
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
