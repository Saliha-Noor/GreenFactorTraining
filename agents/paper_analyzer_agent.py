import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

FAST_MODEL = "llama-3.1-8b-instant"


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def _analyze_chunk(args):
    chunk, source, index, total = args
    prompt = (
        f"Analyze this past paper extract from '{source}'.\n"
        "Identify: topics tested, question types, key terms, difficulty.\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "topics_tested": ["topic1"],\n'
        '  "question_types": ["MCQ"],\n'
        '  "key_terms": ["term1"],\n'
        '  "difficulty": "medium"\n'
        "}\n\n"
        f"Extract:\n{chunk}\n\nJSON only:"
    )
    for attempt in range(3):
        try:
            resp = _client().chat.completions.create(
                model=FAST_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )
            raw = resp.choices[0].message.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            result = json.loads(raw[start:end])
            print(f"  ✓ Chunk {index}/{total}")
            return result
        except Exception as e:
            if "rate_limit" in str(e).lower():
                time.sleep(60)
            else:
                print(f"  ✗ Chunk {index}/{total}: {e}")
                return None
    return None


def run_paper_analyzer_agent(chunks_dir, output_path, progress_callback=None):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("=" * 50)
    log("AGENT 4: PAPER ANALYZER AGENT (parallel)")
    log("=" * 50)

    chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".json")]
    if not chunk_files:
        log("No chunks found. Run Day 1 first.")
        return None

    all_topics = {}
    all_qtypes = {}
    all_terms = {}

    for chunk_file in chunk_files:
        source = chunk_file.replace(".json", "")
        log(f"\nAnalyzing: {source}")

        with open(os.path.join(chunks_dir, chunk_file), "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data.get("chunks", [])
        if not chunks:
            continue

        args_list = [(c, source, i + 1, len(chunks)) for i, c in enumerate(chunks)]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(_analyze_chunk, a) for a in args_list]
            for future in as_completed(futures):
                r = future.result()
                if not r:
                    continue
                for t in r.get("topics_tested", []):
                    if t.strip():
                        all_topics[t] = all_topics.get(t, 0) + 1
                for q in r.get("question_types", []):
                    if q.strip():
                        all_qtypes[q] = all_qtypes.get(q, 0) + 1
                for term in r.get("key_terms", []):
                    if term.strip():
                        all_terms[term] = all_terms.get(term, 0) + 1

    sorted_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)
    sorted_terms = sorted(all_terms.items(), key=lambda x: x[1], reverse=True)

    analysis = {
        "top_topics": [{"topic": t, "frequency": f} for t, f in sorted_topics[:20]],
        "question_type_distribution": all_qtypes,
        "high_frequency_terms": [{"term": t, "count": c} for t, c in sorted_terms[:25]],
        "recommended_focus": [t for t, _ in sorted_topics[:5]],
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    log("\n  ✓ Top topics:")
    for item in analysis["top_topics"][:5]:
        log(f"    - {item['topic']} ({item['frequency']}x)")
    log(f"  ✓ Recommended focus: {', '.join(analysis['recommended_focus'])}")
    log(f"\n✓ Analysis saved: {output_path}")
    return output_path