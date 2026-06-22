import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

QUALITY_MODEL = "llama-3.3-70b-versatile"


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def get_feedback(question, options, correct, user_answer):
    prompt = (
        f"Question: {question}\n"
        f"Correct answer: {correct} — {options.get(correct, '')}\n"
        f"Student answered: {user_answer} — {options.get(user_answer, '')}\n\n"
        "Write 2 clear sentences of feedback. "
        "If wrong: explain the mistake and why the correct answer is right. "
        "If correct: briefly reinforce why it is correct."
    )
    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=QUALITY_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower():
                time.sleep(30)
            else:
                return f"Correct answer: {correct} — {options.get(correct, '')}"
    return f"Correct answer: {correct} — {options.get(correct, '')}"


def run_scoring_agent(
    quiz_dir, scores_dir, feedback_dir,
    user_answers=None, progress_callback=None
):
    """
    user_answers: dict {1: "A", 2: "C", ...} from UI
    If None, runs in terminal interactive mode.
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    os.makedirs(scores_dir, exist_ok=True)
    os.makedirs(feedback_dir, exist_ok=True)

    quiz_path = os.path.join(quiz_dir, "full_quiz.json")
    if not os.path.exists(quiz_path):
        log("No quiz found. Run Day 5 first.")
        return None

    with open(quiz_path) as f:
        quiz_data = json.load(f)

    questions = quiz_data.get("questions", [])
    if not questions:
        log("Quiz is empty.")
        return None

    score = 0
    results = []
    feedback_list = []
    weak_topics = []

    for i, q in enumerate(questions, 1):
        correct = q["answer"]

        if user_answers:
            user_ans = user_answers.get(i, "A")
        else:
            # Terminal mode
            print(f"\nQ{i}/{len(questions)} [{q.get('difficulty','?').upper()}] — {q.get('topic','')}")
            print(q["question"])
            for label, opt in q["options"].items():
                print(f"  {label}: {opt}")
            while True:
                user_ans = input("\nYour answer (A/B/C/D): ").strip().upper()
                if user_ans in ["A", "B", "C", "D"]:
                    break
                print("  Enter A, B, C, or D.")

        is_correct = user_ans == correct
        if is_correct:
            score += 1
        else:
            weak_topics.append(q.get("topic", "Unknown"))

        log(f"  Q{i}: {'✓' if is_correct else '✗'} (You: {user_ans}, Correct: {correct})")

        feedback = get_feedback(q["question"], q["options"], correct, user_ans)

        results.append({
            "q_number": i,
            "topic": q.get("topic", "?"),
            "question": q["question"],
            "correct_answer": correct,
            "user_answer": user_ans,
            "is_correct": is_correct,
            "difficulty": q.get("difficulty", "?"),
        })
        feedback_list.append({
            "q_number": i,
            "topic": q.get("topic", "?"),
            "question": q["question"],
            "feedback": feedback,
            "is_correct": is_correct,
        })

    total = len(questions)
    percent = round((score / total) * 100)
    grade = (
        "Excellent" if percent >= 80 else
        "Good" if percent >= 60 else
        "Needs Work" if percent >= 40 else
        "Revise This Topic"
    )

    # Output 1: Score report
    score_report = {
        "score": score, "total": total, "percent": percent,
        "grade": grade, "weak_topics": list(set(weak_topics)),
        "results": results,
    }
    score_path = os.path.join(scores_dir, "score_report.json")
    with open(score_path, "w") as f:
        json.dump(score_report, f, indent=2)

    # Output 2: Feedback (separate file)
    feedback_out = {
        "total_questions": total, "correct": score,
        "per_question_feedback": feedback_list,
        "topics_to_revise": list(set(weak_topics)),
    }
    feedback_path = os.path.join(feedback_dir, "feedback.json")
    with open(feedback_path, "w") as f:
        json.dump(feedback_out, f, indent=2)

    log(f"\n✓ Score: {score}/{total} ({percent}%) — {grade}")
    log(f"✓ Score report → {score_path}")
    log(f"✓ Feedback     → {feedback_path}")

    return score_report, feedback_out