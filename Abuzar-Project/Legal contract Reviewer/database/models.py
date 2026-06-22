"""SQLAlchemy ORM models for the contract review database."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ClauseType(Base):
    """The 41 CUAD clause types with descriptions and risk categories."""
    __tablename__ = "clause_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    risk_category = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW

    examples = relationship("ClauseExample", back_populates="clause_type", cascade="all, delete-orphan")


class ClauseExample(Base):
    """CUAD-annotated example text spans for each clause type."""
    __tablename__ = "clause_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clause_type_id = Column(Integer, ForeignKey("clause_types.id"), nullable=False, index=True)
    source_contract = Column(String(500), nullable=False)
    text_span = Column(Text, nullable=False)

    clause_type = relationship("ClauseType", back_populates="examples")


class AnalyzedContract(Base):
    """Records of contracts that have been analyzed."""
    __tablename__ = "analyzed_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    page_count = Column(Integer, default=0)
    overall_risk_score = Column(Float, default=0.0)
    parties = Column(Text, default="")
    report_json = Column(Text, default="{}")
