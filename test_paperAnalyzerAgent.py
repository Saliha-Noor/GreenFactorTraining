import os
from dotenv import load_dotenv
from agents.paper_analyzer_agent import run_paper_analyzer_agent

load_dotenv()

print("Testing Day 4 - Paper Analyzer Agent")
print("=" * 50)

result = run_paper_analyzer_agent(
    chunks_dir="data/chunks",
    output_path="data/output/paper_analysis.json"
)

print("\n" + "=" * 50)
if result:
    print("Day 4 SUCCESS! Check data/output/paper_analysis.json")
else:
    print("Failed. Run Day 1 first.")