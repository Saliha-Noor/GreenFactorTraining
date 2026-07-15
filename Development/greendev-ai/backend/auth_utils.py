import os
import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import Header, HTTPException, Depends
from database import get_db
from dotenv import load_dotenv

# Search for .env relative to the location of this file
current_file_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_file_dir, '.env'))
load_dotenv()

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

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set. "
        "Please generate a strong random secret key (e.g. using openssl rand -hex 32) and set it in your environment."
    )

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

def get_current_user(authorization: str = Header(None), x_api_key: str = Header(None)):
    db = next(get_db())
    try:
        # 1. JWT Check
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = verify_jwt(token)
            if payload and "user_id" in payload:
                cursor = db.cursor()
                cursor.execute("SELECT id, email, name, organization, created_at FROM users WHERE id = ?", (payload["user_id"],))
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
                cursor.execute("SELECT id, email, name, organization, created_at FROM users WHERE id = ?", (key_row["user_id"],))
                user = cursor.fetchone()
                if user:
                    return dict(user)

        raise HTTPException(status_code=401, detail="Authentication failed. Log in or provide a valid API Key.")
    finally:
        db.close()

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
    notify_updates: Optional[int] = None
    notify_marketing: Optional[int] = None
    notify_alerts: Optional[int] = None

class ApiKeyGenerateSchema(BaseModel):
    name: Optional[str] = "Default Key"
