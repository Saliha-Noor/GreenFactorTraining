import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

QUALITY_MODEL = "llama-3.3-70b-versatile"


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def _generate_for_topic(args):
    topic_name, notes_text, focus_terms, index, total = args
    prompt = (
        f"Generate 3 MCQ exam questions about '{topic_name}'.\n"
        f"Focus on these high-frequency terms: {', '.join(focus_terms[:8])}\n\n"
        "Rules:\n"
        "- 4 options each: A, B, C, D\n"
        "- Only one correct answer\n"
        "- Mix: 1 easy, 1 medium, 1 hard\n"
        "- Base questions only on the notes below\n"
        "- Include a brief explanation for the correct answer\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "topic": "topic name",\n'
        '  "questions": [\n'
        "    {\n"
        '      "question": "...",\n'
        '      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},\n'
        '      "answer": "A",\n'
        '      "difficulty": "easy",\n'
        '      "explanation": "brief reason"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"Notes:\n{notes_text[:2500]}\n\nJSON only:"
    )
    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=QUALITY_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3,
            )
            raw = resp.choices[0].message.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            result = json.loads(raw[start:end])
            print(f"  ✓ Topic {index}/{total}: {topic_name}")
            return result
        except Exception as e:
            if "rate_limit" in str(e).lower():
                time.sleep(60)
            else:
                print(f"  ✗ Topic {index}/{total}: {e}")
                if attempt == 2:
                    return None
                time.sleep(5)
    return None


def run_quiz_agent(notes_dir, plan_path, analysis_path, quiz_dir, progress_callback=None):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("=" * 50)
    log("AGENT 5: QUIZ MAKER AGENT")
    log("=" * 50)

    os.makedirs(quiz_dir, exist_ok=True)

    # Load plan
    topics = []
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            plan = json.load(f)
        topics = plan.get("topics", [])
        log(f"  Loaded plan: {len(topics)} topics")

    # Load paper analysis
    focus_terms = []
    if os.path.exists(analysis_path):
        with open(analysis_path) as f:
            analysis = json.load(f)
        focus_terms = [t["term"] for t in analysis.get("high_frequency_terms", [])]
        log(f"  Loaded analysis: {len(focus_terms)} high-frequency terms")

    # Load notes
    notes_map = {}
    for nf in os.listdir(notes_dir):
        if nf.endswith(".md"):
            with open(os.path.join(notes_dir, nf), "r", encoding="utf-8") as f:
                notes_map[nf.replace("_notes.md", "")] = f.read()

    if not notes_map:
        log("No notes. Run Day 2 first.")
        return []

    # Build args for each topic
    if topics:
        default_notes = list(notes_map.values())[0]
        args_list = []
        for i, t in enumerate(topics):
            src = t.get("source", list(notes_map.keys())[0])
            notes = notes_map.get(src, default_notes)
            args_list.append((t["name"], notes, focus_terms, i + 1, len(topics)))
    else:
        args_list = [
            (src, txt, focus_terms, i + 1, len(notes_map))
            for i, (src, txt) in enumerate(notes_map.items())
        ]

    log(f"\n  Generating questions for {len(args_list)} topics in parallel...")

    all_questions = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_generate_for_topic, a) for a in args_list]
        for future in as_completed(futures):
            result = future.result()
            if result:
                qs = result.get("questions", [])
                topic_name = result.get("topic", "")
                for q in qs:
                    q["topic"] = topic_name
                all_questions.extend(qs)

    if not all_questions:
        log("  ✗ No questions generated.")
        return []

    # Save full quiz
    quiz_data = {
        "total_questions": len(all_questions),
        "plan_used": bool(topics),
        "analysis_used": bool(focus_terms),
        "questions": all_questions,
    }
    quiz_path = os.path.join(quiz_dir, "full_quiz.json")
    with open(quiz_path, "w") as f:
        json.dump(quiz_data, f, indent=2)

    # Save practice paper (grouped by difficulty)
    easy = [q for q in all_questions if q.get("difficulty") == "easy"]
    medium = [q for q in all_questions if q.get("difficulty") == "medium"]
    hard = [q for q in all_questions if q.get("difficulty") == "hard"]

    practice = {
        "title": "Practice Exam Paper",
        "instructions": "Answer all questions. Time allowed: 60 minutes.",
        "total_marks": len(all_questions),
        "sections": [],
    }
    if easy:
        practice["sections"].append({"section": "Section A — Easy", "marks": len(easy), "questions": easy})
    if medium:
        practice["sections"].append({"section": "Section B — Medium", "marks": len(medium), "questions": medium})
    if hard:
        practice["sections"].append({"section": "Section C — Hard", "marks": len(hard), "questions": hard})

    practice_path = os.path.join(quiz_dir, "practice_paper.json")
    with open(practice_path, "w") as f:
        json.dump(practice, f, indent=2)

    log(f"\n  ✓ Full quiz: {len(all_questions)} questions → {quiz_path}")
    log(f"  ✓ Practice paper → {practice_path}")
    log(f"  ✓ Breakdown: {len(easy)} easy | {len(medium)} medium | {len(hard)} hard")
    return [quiz_path, practice_path]