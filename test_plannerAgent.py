import os
from dotenv import load_dotenv
from agents.planner_agent import run_planner_agent

load_dotenv()

print("Testing Day 3 - Planner Agent")
print("=" * 50)

os.makedirs("data/output", exist_ok=True)

result = run_planner_agent(
    notes_dir="data/output/notes",
    output_path="data/output/plan.json"
)

print("\n" + "=" * 50)
if result:
    print("Day 3 SUCCESS! Check data/output/plan.json")
else:
    print("Failed. Run Day 2 first.")