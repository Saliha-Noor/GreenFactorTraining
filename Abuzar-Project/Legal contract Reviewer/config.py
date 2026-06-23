"""Central configuration for the Multi-Agent Legal Contract Review System."""

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
CUAD_DIR = BASE_DIR / "cuad_data"
DB_PATH = BASE_DIR / "contract_review.db"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
CUAD_DIR.mkdir(exist_ok=True)

# LLM Configuration (OpenAI-compatible gateway)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gateway-claude-opus-4-8")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://unlimited.surf/api/v1")

# Database
DATABASE_URL = f"sqlite:///{DB_PATH}"

# CUAD Dataset
CUAD_JSON_URL = "https://raw.githubusercontent.com/TheAtticusProject/cuad/main/CUADv1.json"
CUAD_JSON_PATH = CUAD_DIR / "CUAD_v1" / "CUAD_v1" / "CUAD_v1.json"

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
    """Make an API call to the configured Anthropic-compatible gateway."""
    import requests
    url = "https://unlimited.surf/v1/messages"
    headers = {
        "x-api-key": LLM_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    res_json = response.json()
    return res_json["content"][0]["text"]


