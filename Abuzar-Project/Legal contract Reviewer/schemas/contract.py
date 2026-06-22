"""Pydantic models that enforce the structured JSON output schema."""

from pydantic import BaseModel, Field
from typing import List, Optional


class IdentifiedClause(BaseModel):
    """A single clause identified in the contract, grounded in the actual text."""
    clause_type: str = Field(..., description="One of the 41 CUAD clause types")
    text_excerpt: str = Field(..., description="EXACT verbatim text quoted from the contract")
    page_number: int = Field(..., ge=1, description="Page where the clause appears")
    section: str = Field(default="", description="Section or paragraph reference")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class RiskAssessment(BaseModel):
    """Risk evaluation for a specific identified clause."""
    clause_type: str = Field(..., description="The CUAD clause type being assessed")
    risk_level: str = Field(..., description="HIGH, MEDIUM, or LOW")
    risk_score: int = Field(..., ge=1, le=10, description="Risk severity from 1 (safe) to 10 (dangerous)")
    risk_rationale: str = Field(..., description="Clear explanation of why this clause is risky")
    negotiation_tip: str = Field(..., description="Actionable suggestion for negotiating this clause")
    source_text: str = Field(..., description="The clause text that triggered this risk flag")


class ContractReport(BaseModel):
    """The final structured report — the system's main output."""
    document_name: str = Field(default="Unknown Contract")
    parties: List[str] = Field(default_factory=list)
    agreement_date: Optional[str] = None
    effective_date: Optional[str] = None
    governing_law: Optional[str] = None
    overall_risk_score: float = Field(..., ge=1.0, le=10.0)
    risk_summary: str = Field(default="", description="One-line risk verdict")
    total_clauses_found: int = Field(default=0)
    high_risk_count: int = Field(default=0)
    medium_risk_count: int = Field(default=0)
    low_risk_count: int = Field(default=0)
    identified_clauses: List[IdentifiedClause] = Field(default_factory=list)
    risk_assessments: List[RiskAssessment] = Field(default_factory=list)
    executive_summary: str = Field(default="")
    recommendations: List[str] = Field(default_factory=list)
    analysis_timestamp: str = Field(default="")
    page_count: int = Field(default=0)
