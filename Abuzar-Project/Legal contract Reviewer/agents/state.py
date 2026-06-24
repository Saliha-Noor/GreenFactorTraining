from typing import TypedDict, List

# Shared pipeline execution state passed between all agents
class PipelineState(TypedDict, total=False):
    file_path: str
    raw_text: str
    cleaned_pages: List[dict]
    page_count: int
    identified_clauses: List[dict]
    risk_assessments: List[dict]
    overall_risk_score: float
    final_report: dict
    status: str
    errors: List[str]
