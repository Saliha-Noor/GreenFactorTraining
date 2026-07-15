from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()

@router.get("/help")
def get_help_articles():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_index, category_name, intro, heading, body FROM help_articles ORDER BY category_index, display_order")
        rows = cursor.fetchall()
        
        grouped = {}
        for r in rows:
            idx = r["category_index"]
            if idx not in grouped:
                grouped[idx] = {
                    "category_index": idx,
                    "title": r["category_name"],
                    "intro": r["intro"] or "",
                    "sections": []
                }
            grouped[idx]["sections"].append({
                "heading": r["heading"],
                "body": r["body"]
            })
        return list(grouped.values())
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/faq")
def get_faq_list():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_index, question, answer FROM faqs ORDER BY category_index, display_order")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

@router.get("/benchmarks/languages")
def get_benchmark_notes():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT language, factor, energy_notes, runtime_notes, rapl_notes FROM benchmark_notes ORDER BY display_order")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()

@router.get("/samples")
def get_sample_scripts():
    db = next(get_db())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT filename, score, verdict, color, source_code FROM sample_scripts ORDER BY display_order")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()
