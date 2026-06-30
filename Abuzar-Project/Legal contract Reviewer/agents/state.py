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
    contract_type: str
    missing_clause_analysis: List[dict]
    completeness_score: float
    conflict_analysis: List[dict]
    consistency_score: float
    consistency_explanation: str
    final_report: dict
    status: str
    errors: List[str]
