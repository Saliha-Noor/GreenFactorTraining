"""
agents/practice_paper_agent.py

Generates a structured practice paper from:
- Chunked raw content (chunks_dir)
- Processed notes (notes_dir)
- Paper analysis JSON (analysis_path)   ← output of paper_analyzer_agent
- Lesson plan JSON (plan_path)          ← output of lesson_plan_agent (optional)
- Writes final paper to output_path     ← e.g. data/output/practice_paper/paper.json

Paper format mirrors your GitHub past papers:
  - Sections with marks-per-question
  - Short-answer and long-answer questions only (NO MCQs)
  - Total marks shown per section and overall
  - Estimated time shown

Uses Groq (same GROQ_API_KEY as your other agents) — no Anthropic key needed.
"""

import os
import json
import re
import time
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

QUALITY_MODEL = "llama-3.3-70b-versatile"  # same model your planner_agent/evaluater_agent use


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_json(path: str | Path) -> dict | list | None:
    p = Path(path)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _read_text_files(directory: str | Path, extensions=(".txt", ".md")) -> str:
    """Concatenate all text files in a directory into one string (truncated to ~12 000 chars)."""
    parts = []
    for fp in sorted(Path(directory).rglob("*")):
        if fp.suffix.lower() in extensions and fp.is_file():
            try:
                parts.append(f"--- {fp.name} ---\n{fp.read_text(encoding='utf-8', errors='ignore')}")
            except Exception:
                pass
    combined = "\n\n".join(parts)
    return combined[:12000]  # stay well inside context


def _build_system_prompt() -> str:
    return """You are an expert academic exam paper writer.
Your job is to generate a realistic, challenging practice exam paper based on provided study notes and a paper analysis.

STRICT RULES:
1. NO multiple-choice questions (MCQs) of any kind.
2. All questions must be short-answer or long-answer / essay style.
3. Follow the section structure and marks weighting from the paper analysis exactly.
4. Each question must have:
   - A question number
   - The question text
   - Marks allocated  (e.g. [5 marks])
   - Difficulty: easy / medium / hard
5. Distribute difficulty roughly 30% easy, 30% medium, 40% hard.
6. Questions must be answerable from the provided notes — do not invent unrelated content.
7. Return ONLY valid JSON — no markdown fences, no preamble, no explanation.

OUTPUT FORMAT (strict JSON):
{
  "title": "Practice Paper — <subject>",
  "total_marks": <int>,
  "estimated_time_minutes": <int>,
  "instructions": "<brief general instructions string>",
  "sections": [
    {
      "section_label": "Section A",
      "section_title": "<e.g. Short Answer>",
      "marks": <int>,
      "questions": [
        {
          "number": "1",
          "text": "<question text>",
          "marks": <int>,
          "difficulty": "easy|medium|hard",
          "sub_questions": []   // optional list of {"label":"a","text":"...","marks":int}
        }
      ]
    }
  ]
}
"""


def _build_user_prompt(notes_text: str, analysis: dict | None, plan: dict | None) -> str:
    analysis_str = json.dumps(analysis, indent=2) if analysis else "No analysis available — infer structure from notes."
    plan_str = json.dumps(plan, indent=2) if plan else "No lesson plan available."

    return f"""PAPER ANALYSIS (structure, weighting, question types from past papers):
{analysis_str}

LESSON PLAN (topics covered):
{plan_str}

STUDY NOTES (source material — questions must come from this):
{notes_text}

Generate a full practice paper following the format in the system prompt.
Use the paper analysis to decide number of sections, marks per section, and question style.
If the analysis is missing, create a sensible 3-section paper (Section A ~30 marks short answer, Section B ~40 marks medium, Section C ~30 marks long answer).
Total marks should match the analysis total or default to 100.
"""


# ---------------------------------------------------------------------------
# Main entry point (called from app.py)
# ---------------------------------------------------------------------------

def run_practice_paper_agent(
    chunks_dir: str,
    notes_dir: str,
    analysis_path: str,
    plan_path: str,
    output_path: str,
) -> dict:
    """
    Generate a practice paper and write it to output_path as JSON.

    Returns the paper dict on success, or raises RuntimeError on failure.
    """

    # 1. Load inputs
    notes_text = _read_text_files(notes_dir) or _read_text_files(chunks_dir)
    if not notes_text:
        raise RuntimeError("No notes or chunks found. Upload and process your notes first.")

    analysis = _read_json(analysis_path)
    plan = _read_json(plan_path)

    # 2. Call Groq (with retry/rate-limit handling, same pattern as your other agents)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(notes_text, analysis, plan)

    raw = None
    last_error = None
    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=QUALITY_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=6000,
                temperature=0.3,
            )
            raw = resp.choices[0].message.content.strip()
            break
        except Exception as e:
            last_error = e
            if "rate_limit" in str(e).lower():
                print(f"  Rate limit hit, waiting 30s... (attempt {attempt + 1}/3)")
                time.sleep(30)
            else:
                print(f"  Attempt {attempt + 1}/3 failed: {e}")
                time.sleep(5)

    if raw is None:
        raise RuntimeError(f"Groq call failed after 3 attempts: {last_error}")

    # 3. Parse JSON (strip any accidental fences)
    raw_clean = re.sub(r"^```[a-z]*\n?", "", raw)
    raw_clean = re.sub(r"\n?```$", "", raw_clean).strip()

    try:
        start = raw_clean.find("{")
        end = raw_clean.rfind("}") + 1
        paper = json.loads(raw_clean[start:end])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Groq returned invalid JSON: {e}\n\nRaw output (first 500 chars):\n{raw[:500]}")

    # 4. Validate top-level keys
    required = {"title", "total_marks", "sections"}
    missing = required - set(paper.keys())
    if missing:
        raise RuntimeError(f"Paper JSON is missing required keys: {missing}")

    # 5. Write output
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(paper, f, indent=2, ensure_ascii=False)

    return paper


# ---------------------------------------------------------------------------
# Plain-text formatter (used by app.py for .txt download)
# ---------------------------------------------------------------------------

def paper_to_text(paper: dict) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(paper.get("title", "Practice Paper").upper().center(70))
    lines.append("=" * 70)
    lines.append(f"Total Marks : {paper.get('total_marks', '?')}")
    lines.append(f"Time        : {paper.get('estimated_time_minutes', '?')} minutes")
    instr = paper.get("instructions", "")
    if instr:
        lines.append(f"\nInstructions: {instr}")
    lines.append("")

    for sec in paper.get("sections", []):
        lines.append("-" * 70)
        lines.append(
            f"{sec.get('section_label','Section')}  —  {sec.get('section_title','')}  "
            f"[{sec.get('marks','?')} marks]"
        )
        lines.append("-" * 70)
        for q in sec.get("questions", []):
            num = q.get("number", "?")
            text = q.get("text", "")
            marks = q.get("marks", "?")
            diff = q.get("difficulty", "")
            lines.append(f"\nQ{num}. {text}  [{marks} marks]  ({diff})")
            for sub in q.get("sub_questions", []):
                label = sub.get("label", "")
                stext = sub.get("text", "")
                smarks = sub.get("marks", "?")
                lines.append(f"    ({label}) {stext}  [{smarks} marks]")
        lines.append("")

    lines.append("=" * 70)
    lines.append("END OF PAPER")
    lines.append("=" * 70)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI test  (works whether you run it from study_agent/ root or from agents/)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # Find the project root automatically (the folder that contains "data/"),
    # so this works whether you run "python practice_paper_agent.py" from
    # study_agent/agents OR from study_agent/ itself.
    here = Path(__file__).resolve().parent           # .../study_agent/agents
    if (here / "data").exists():
        project_root = here                            # running from study_agent/ root
    else:
        project_root = here.parent                     # running from study_agent/agents

    data_dir = project_root / "data"

    chunks = str(data_dir / "chunks")
    notes = str(data_dir / "output" / "notes")
    analysis = str(data_dir / "output" / "paper_analysis.json")
    plan = str(data_dir / "output" / "plan.json")
    out = str(data_dir / "output" / "practice_paper" / "paper.json")

    print(f"Project root detected: {project_root}")
    print(f"  chunks_dir : {chunks}")
    print(f"  notes_dir  : {notes}")
    print(f"  analysis   : {analysis}")
    print(f"  plan       : {plan}")
    print(f"  output     : {out}\n")

    print("Running practice paper agent...")
    try:
        paper = run_practice_paper_agent(chunks, notes, analysis, plan, out)
        print(f"✓ Paper written to {out}")
        print(f"  Title        : {paper['title']}")
        print(f"  Total marks  : {paper['total_marks']}")
        print(f"  Sections     : {len(paper['sections'])}")
        total_q = sum(len(s.get('questions', [])) for s in paper['sections'])
        print(f"  Questions    : {total_q}")
    except RuntimeError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)