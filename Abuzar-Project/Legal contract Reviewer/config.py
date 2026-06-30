import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(override=True)

# Define directories and file paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
CUAD_DIR = BASE_DIR / "cuad_data"
DB_PATH = BASE_DIR / "contract_review.db"

# Create required directories
UPLOAD_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
CUAD_DIR.mkdir(exist_ok=True)

# Configure LLM settings (Groq API — OpenAI-compatible)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

# Define database URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Define CUAD dataset URLs and paths
CUAD_JSON_URL = "https://raw.githubusercontent.com/TheAtticusProject/cuad/main/CUADv1.json"
CUAD_JSON_PATH = CUAD_DIR / "CUAD_v1" / "CUAD_v1.json"

# Call the Groq LLM via OpenAI-compatible chat completions API
def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
    import requests
    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]
