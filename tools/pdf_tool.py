import pdfplumber
import os
import json


def read_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def process_pdf(filepath, output_dir):
    filename = os.path.basename(filepath).replace(".pdf", "")
    print(f"  Reading: {filename}")

    text = read_pdf(filepath)

    if not text.strip():
        print(f"  Warning: No text found in {filename}")
        return None

    chunks = chunk_text(text)

    output = {
        "source": filename,
        "total_chunks": len(chunks),
        "chunks": chunks
    }

    out_path = os.path.join(output_dir, f"{filename}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"  Done: {len(chunks)} chunks saved")
    return out_path
def process_text(text, filename, output_dir):
    print(f"  Chunking: {filename}")

    if not text.strip():
        print(f"  Warning: No text found in {filename}")
        return None

    chunks = chunk_text(text)

    output = {
        "source": filename,
        "total_chunks": len(chunks),
        "chunks": chunks
    }

    out_path = os.path.join(output_dir, f"{filename}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"  Done: {len(chunks)} chunks saved")
    return out_path
def process_text(text, filename, output_dir):
    print(f"  Chunking: {filename}")
    if not text or not text.strip():
        print(f"  Warning: Empty text for {filename}")
        return None
    chunks = chunk_text(text)
    if not chunks:
        return None
    output = {
        "source": filename,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{filename}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {len(chunks)} chunks → {os.path.basename(out_path)}")
    return out_path