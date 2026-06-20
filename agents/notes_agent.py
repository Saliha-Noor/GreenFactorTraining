import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Fast model for high-volume chunk summarization
FAST_MODEL = "llama-3.1-8b-instant"


def _client():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY not set in .env")
    return Groq(api_key=key)


def _summarise_chunk(args):
    chunk, source, index, total = args
    prompt = (
        f"You are a study assistant. Extract clear study notes from "
        f"this extract of '{source}'.\n"
        "Use bullet points. Include: key concepts, definitions, "
        "formulas, rules. Be concise. Do not add anything not in the text.\n\n"
        f"Extract:\n{chunk}\n\nBullet point notes:"
    )
    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=FAST_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
            )
            print(f"  ✓ Chunk {index}/{total}")
            return index, resp.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                wait = 60 if attempt == 0 else 30
                print(f"  Rate limit hit. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  ✗ Chunk {index}/{total}: {e}")
                return index, None
    return index, None


def run_notes_agent(chunks_dir, notes_dir, progress_callback=None):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("=" * 50)
    log("AGENT 2: NOTES AGENT (parallel, fast model)")
    log("=" * 50)

    os.makedirs(notes_dir, exist_ok=True)
    chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".json")]

    if not chunk_files:
        log("No chunk files. Run Day 1 first.")
        return []

    notes_files = []

    for chunk_file in chunk_files:
        source = chunk_file.replace(".json", "")
        log(f"\nProcessing: {source}")

        with open(os.path.join(chunks_dir, chunk_file), "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data.get("chunks", [])
        total = len(chunks)
        if not chunks:
            log(f"  No chunks in {source}. Skipping.")
            continue

        log(f"  {total} chunks — 5 parallel workers...")
        args_list = [(chunk, source, i + 1, total) for i, chunk in enumerate(chunks)]
        results = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_summarise_chunk, a): a for a in args_list}
            for future in as_completed(futures):
                try:
                    index, summary = future.result()
                    if summary:
                        results[index] = summary
                except Exception as e:
                    log(f"  ✗ Error: {e}")

        if not results:
            log(f"  ✗ No summaries for {source}")
            continue

        lines = [f"# Study Notes: {source}\n"]
        for i in sorted(results.keys()):
            lines.append(f"\n## Section {i}\n{results[i]}\n")

        out_path = os.path.join(notes_dir, f"{source}_notes.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        log(f"  ✓ Saved: {os.path.basename(out_path)}")
        notes_files.append(out_path)

    log(f"\n✓ Notes Agent done! {len(notes_files)} file(s) created.")
    return notes_files