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

# Groq LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Database
DATABASE_URL = f"sqlite:///{DB_PATH}"

# CUAD Dataset
CUAD_JSON_URL = "https://raw.githubusercontent.com/TheAtticusProject/cuad/main/CUADv1.json"
CUAD_JSON_PATH = CUAD_DIR / "CUAD_v1" / "CUAD_v1" / "CUAD_v1.json"
