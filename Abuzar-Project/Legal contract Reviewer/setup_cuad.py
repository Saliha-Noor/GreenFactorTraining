"""Downloads the CUAD dataset and seeds the SQLite database.

Run this once before starting the server:
    python setup_cuad.py
"""

import sys
import requests
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CUAD_JSON_URL, CUAD_JSON_PATH, CUAD_DIR
from database.connection import init_db, SessionLocal
from database.seed_cuad import seed_clause_types, seed_cuad_examples


def download_cuad():
    """Download the CUAD v1 JSON from GitHub if not already present."""
    if CUAD_JSON_PATH.exists():
        size_mb = CUAD_JSON_PATH.stat().st_size / (1024 * 1024)
        print(f"[OK] CUAD JSON already downloaded ({size_mb:.1f} MB)")
        return

    CUAD_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[...] Downloading CUAD dataset from GitHub...")
    print(f"      URL: {CUAD_JSON_URL}")
    print(f"      This may take a few minutes (~25 MB)...")

    try:
        response = requests.get(CUAD_JSON_URL, stream=True, timeout=300)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(CUAD_JSON_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r      Progress: {pct:.1f}%  ({downloaded // 1024} KB)", end="", flush=True)

        print(f"\n[OK] Downloaded to {CUAD_JSON_PATH}")

    except requests.RequestException as exc:
        print(f"\n[ERROR] Download failed: {exc}")
        print("       You can manually download from:")
        print(f"       {CUAD_JSON_URL}")
        print(f"       Save as: {CUAD_JSON_PATH}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  CUAD DATASET SETUP")
    print("=" * 60)

    # Step 1: Download CUAD JSON
    print("\n[Step 1/3] Downloading CUAD dataset...")
    download_cuad()

    # Step 2: Initialize database
    print("\n[Step 2/3] Initializing database...")
    init_db()
    print("  [OK] Database tables created")

    # Step 3: Seed data
    print("\n[Step 3/3] Seeding database with CUAD data...")
    db = SessionLocal()
    try:
        seed_clause_types(db)
        seed_cuad_examples(db, CUAD_JSON_PATH, max_examples_per_type=50)
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("  You can now run: python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
