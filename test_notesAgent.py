import os
from dotenv import load_dotenv
from agents.notes_agent import run_notes_agent

load_dotenv()

print("Testing Day 2 - Notes Agent")
print("="*50)

os.makedirs("data/output/notes", exist_ok=True)

notes_files = run_notes_agent(
    chunks_dir="data/chunks",
    notes_dir="data/output/notes"
)

print("\n" + "="*50)
if notes_files:
    print(f"Day 2 SUCCESS! {len(notes_files)} notes file(s) created.")
    print("Check data/output/notes/ to read them.")
else:
    print("No notes created. Make sure Day 1 ran first.")