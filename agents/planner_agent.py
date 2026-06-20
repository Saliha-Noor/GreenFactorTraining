import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Quality model for planning — needs good reasoning
QUALITY_MODEL = "llama-3.3-70b-versatile"


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def _build_plan(all_notes_text, sources):
    prompt = (
        "You are an expert academic study planner.\n"
        f"Sources: {', '.join(sources)}\n\n"
        "Analyze these study notes and identify every topic. "
        "Return ONLY valid JSON, no extra text:\n"
        "{\n"
        '  "total_topics": 5,\n'
        '  "total_study_time": "4 hours",\n'
        '  "topics": [\n'
        "    {\n"
        '      "id": 1,\n'
        '      "name": "topic name",\n'
        '      "source": "filename",\n'
        '      "priority": "high",\n'
        '      "exam_weight": "25%",\n'
        '      "estimated_study_time": "45 mins",\n'
        '      "key_concepts": ["concept1", "concept2"],\n'
        '      "study_order": 1\n'
        "    }\n"
        "  ],\n"
        '  "recommended_order": [1, 2, 3]\n'
        "}\n\n"
        "Priority: high=fundamental/frequently tested, "
        "medium=important, low=supplementary.\n\n"
        f"Notes:\n{all_notes_text[:5000]}\n\nJSON only:"
    )

    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=QUALITY_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2,
            )
            raw = resp.choices[0].message.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start == -1:
                raise ValueError("No JSON found")
            plan = json.loads(raw[start:end])
            plan["total_topics"] = len(plan.get("topics", []))
            return plan
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if "rate_limit" in str(e).lower():
                time.sleep(60)
            else:
                time.sleep(5)
    return None


def run_planner_agent(notes_dir, output_path, progress_callback=None):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("=" * 50)
    log("AGENT 3: PLANNER AGENT")
    log("=" * 50)

    notes_files = [f for f in os.listdir(notes_dir) if f.endswith(".md")]
    if not notes_files:
        log("No notes found. Run Day 2 first.")
        return None

    all_text = ""
    sources = []
    for nf in notes_files:
        src = nf.replace("_notes.md", "")
        sources.append(src)
        with open(os.path.join(notes_dir, nf), "r", encoding="utf-8") as f:
            all_text += f"\n\n=== {src} ===\n" + f.read()

    log(f"  Read {len(notes_files)} notes files. Sending to Groq...")
    plan = _build_plan(all_text, sources)

    if not plan:
        log("  ✗ Planning failed.")
        return None

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    log(f"\n  ✓ {plan['total_topics']} topics found")
    log(f"  ✓ Total study time: {plan.get('total_study_time', 'N/A')}")
    log("\n  Study order:")
    for t in sorted(plan.get("topics", []), key=lambda x: x.get("study_order", 99)):
        p = t.get("priority", "?").upper()
        log(f"    {t['study_order']}. [{p}] {t['name']} — {t.get('estimated_study_time','?')}")

    log(f"\n✓ Plan saved: {output_path}")
    return output_path