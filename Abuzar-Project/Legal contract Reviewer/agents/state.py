"""Shared LangGraph state definition for the multi-agent pipeline."""

from typing import TypedDict, List


class PipelineState(TypedDict, total=False):
    """State passed through the LangGraph pipeline from agent to agent."""

    # ── Input ──
    file_path: str

    # ── Agent 1 (Parser) output ──
    raw_text: str
    cleaned_pages: List[dict]   # [{"page": 1, "text": "..."}, ...]
    page_count: int

    # ── Agent 2 (Classifier) output ──
    identified_clauses: List[dict]

    # ── Agent 3 (Risk Analyzer) output ──
    risk_assessments: List[dict]
    overall_risk_score: float

    # ── Agent 4 (Report Generator) output ──
    final_report: dict

    # ── Pipeline metadata ──
    status: str
    errors: List[str]
