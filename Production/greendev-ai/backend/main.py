"""
GreenDev AI — FastAPI Backend
Orchestrates all agents and exposes REST endpoints for the React frontend.
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, billing, cms, analysis

app = FastAPI(title="GreenDev AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local preview
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(cms.router)
app.include_router(analysis.router)

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Initialize DB on start
init_db()
