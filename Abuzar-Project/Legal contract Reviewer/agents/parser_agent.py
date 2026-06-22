"""Agent 1 — The Parser: Extracts and cleans text from uploaded PDF contracts.

This agent is fully deterministic (no LLM calls) so there is zero hallucination risk.
"""

import re
from PyPDF2 import PdfReader
from agents.state import PipelineState


def clean_text(text: str) -> str:
    """Clean raw PDF-extracted text into readable paragraphs."""
    # Fix hyphenated line breaks (e.g. "agree-\nment" → "agreement")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Remove common PDF artifacts
    text = re.sub(r"Page \d+ of \d+", "", text)
    text = re.sub(r"\x0c", "", text)  # form-feed characters
    # Clean up individual lines
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned)


def parser_agent(state: PipelineState) -> dict:
    """
    Agent 1 entry-point.

    Reads the PDF at `state['file_path']`, extracts text page-by-page,
    cleans it, and returns the result for downstream agents.
    """
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
