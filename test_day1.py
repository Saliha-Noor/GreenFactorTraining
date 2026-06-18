import os
from dotenv import load_dotenv
from agents.fetcher_agent import run_fetcher_agent

load_dotenv()

print("Testing Day 1 - Fetcher Agent")
print("="*50)

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    print(f"Groq API key loaded: {api_key[:8]}...")
else:
    print("WARNING: Groq API key not found. Check your .env file.")

for folder in ["data/raw", "data/chunks", "data/output"]:
    if os.path.exists(folder):
        print(f"Folder exists: {folder}")
    else:
        print(f"Missing folder: {folder} - creating it now")
        os.makedirs(folder)

print("\nRunning Fetcher Agent...")
github_repo = os.getenv("GITHUB_REPO") or None

chunk_files = run_fetcher_agent(
    raw_dir="data/raw",
    chunks_dir="data/chunks",
    github_repo=github_repo
)

print("\n" + "="*50)
if chunk_files:
    print(f"Day 1 SUCCESS! {len(chunk_files)} file(s) processed.")
    print("Check data/chunks/ to see the output.")
else:
    print("No files processed. Add a PDF to data/raw/ and try again.")