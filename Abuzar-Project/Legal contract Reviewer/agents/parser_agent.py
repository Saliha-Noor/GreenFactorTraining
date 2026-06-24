import re
from PyPDF2 import PdfReader
from agents.state import PipelineState

# Clean up raw text formatting, spacing, and hyphens
def clean_text(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"Page \d+ of \d+", "", text)
    text = re.sub(r"\x0c", "", text)
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned)

# Extract and clean plain text from PDF document
def parser_agent(state: PipelineState) -> dict:
    file_path = state["file_path"]
    errors: list[str] = list(state.get("errors", []))

    try:
        reader = PdfReader(file_path)
    except Exception as exc:
        errors.append(f"PDF parsing failed: {exc}")
        return {
            "raw_text": "",
            "cleaned_pages": [],
            "page_count": 0,
            "status": "parse_error",
            "errors": errors,
        }

    pages: list[dict] = []
    full_text_parts: list[str] = []

    # Loop pages and build clean text array
    for idx, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        cleaned = clean_text(raw)
        if cleaned:
            pages.append({"page": idx, "text": cleaned})
            full_text_parts.append(cleaned)

    raw_text = "\n\n".join(full_text_parts)

    print(f"  [Parser] Extracted {len(pages)} pages, {len(raw_text)} characters")

    return {
        "raw_text": raw_text,
        "cleaned_pages": pages,
        "page_count": len(pages),
        "status": "parsed",
        "errors": errors,
    }
