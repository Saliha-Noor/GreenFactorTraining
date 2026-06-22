import os
from dotenv import load_dotenv
from agents.evaluater_agent import run_scoring_agent

load_dotenv()

print("Testing Day 6 - Evaluator Agent")
print("=" * 50)

os.makedirs("data/output/scores", exist_ok=True)
os.makedirs("data/output/feedback", exist_ok=True)

result = run_scoring_agent(
    quiz_dir="data/output/quiz",
    scores_dir="data/output/scores",
    feedback_dir="data/output/feedback",
    user_answers=None  # Terminal mode
)

print("\n" + "=" * 50)
if result:
    print("Day 6 SUCCESS!")
    print("Score → data/output/scores/score_report.json")
    print("Feedback → data/output/feedback/feedback.json")
else:
    print("Failed. Run Day 5 first.")