import os
from dotenv import load_dotenv
from agents.quiz_agent import run_quiz_agent

load_dotenv()

print("Testing Day 5 - Quiz Maker Agent")
print("=" * 50)

os.makedirs("data/output/quiz", exist_ok=True)

results = run_quiz_agent(
    notes_dir="data/output/notes",
    plan_path="data/output/plan.json",
    analysis_path="data/output/paper_analysis.json",
    quiz_dir="data/output/quiz"
)

print("\n" + "=" * 50)
if results:
    print(f"Day 5 SUCCESS! {len(results)} file(s) created.")
    print("Check data/output/quiz/")
else:
    print("Failed. Run Days 2-4 first.")