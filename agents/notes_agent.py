import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarise_chunk(chunk, source):
    prompt = f"""You are a study assistant. Read this extract from '{source}' and write clear, concise study notes.
Include: key concepts, definitions, important points, and any formulas or rules.
Format as bullet points.

Extract:
{chunk}

Study notes:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def run_notes_agent(chunks_dir, notes_dir):
    print("\n" + "="*50)
    print("AGENT 2: NOTES AGENT")
    print("="*50)

    os.makedirs(notes_dir, exist_ok=True)
    chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".json")]

    if not chunk_files:
        print("No chunk files found. Run Day 1 first.")
        return []

    print(f"\nFound {len(chunk_files)} chunk file(s) to process")
    notes_files = []

    for chunk_file in chunk_files:
        source_name = chunk_file.replace(".json", "")
        print(f"\nProcessing: {source_name}")

        with open(os.path.join(chunks_dir, chunk_file), "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data["chunks"]
        all_notes = [f"# Study Notes: {source_name}\n"]

        for i, chunk in enumerate(chunks, 1):
            print(f"  Summarising chunk {i}/{len(chunks)}...")
            summary = summarise_chunk(chunk, source_name)
            all_notes.append(f"\n## Section {i}\n{summary}\n")

        notes_content = "\n".join(all_notes)
        out_path = os.path.join(notes_dir, f"{source_name}_notes.md")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(notes_content)

        print(f"  Notes saved: {out_path}")
        notes_files.append(out_path)

    print(f"\nNotes Agent done! {len(notes_files)} notes file(s) created.")
    return notes_files