from pydantic import BaseModel, Field
from typing import List, Optional

# Structured Pydantic model for clause findings
class IdentifiedClause(BaseModel):
    clause_type: str = Field(description="The matching type out of the 41 CUAD classes")
    text_excerpt: str = Field(description="The verbatim contract excerpt")
    page_number: int = Field(description="1-based page number where found")
    section: Optional[str] = Field(None, description="Section heading or title")
    confidence: float = Field(description="AI classification probability rating (0.0 to 1.0)")

# Structured Pydantic model for risk assessments
class RiskAssessment(BaseModel):
    clause_type: str = Field(description="CUAD clause type name")
    source_text: str = Field(description="Verification source excerpt")
    page_number: int = Field(description="Page location index")
    risk_score: int = Field(description="Assessment risk value rating (1 to 10)")
    risk_level: str = Field(description="Risk classification level (LOW / MEDIUM / HIGH)")
    risk_rationale: str = Field(description="Summary detailing the evaluated risks")
    negotiation_tip: str = Field(description="Actionable mitigation suggestions")

# Structured Pydantic model for finalized report payload
class ContractAnalysisReport(BaseModel):
    document_name: str = Field(description="Formal title of contract or derived filename")
    parties: List[str] = Field(description="Detected signing contract entities list")
    agreement_date: Optional[str] = Field(None, description="Effective or signing agreement date")
    governing_law: Optional[str] = Field(None, description="Jurisdictional governing legal territory")
    executive_summary: str = Field(description="Summary report detail statements")
    risk_summary: str = Field(description="High-level risk rating summary sentence")
    overall_risk_score: float = Field(description="Average mathematical risk calculation")
    high_risk_count: int = Field(description="Number of high risk findings")
    medium_risk_count: int = Field(description="Number of medium risk findings")
    low_risk_count: int = Field(description="Number of low risk findings")
    analysis_timestamp: str = Field(description="ISO report compilation date stamp")
    identified_clauses: List[IdentifiedClause] = Field(description="List of detected clauses")
    risk_assessments: List[RiskAssessment] = Field(description="List of evaluated risk findings")
