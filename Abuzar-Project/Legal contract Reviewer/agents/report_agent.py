"""Agent 4 — The Report Generator: Assembles the final structured JSON report.

All data comes from prior agents. The LLM is used ONLY to generate the
executive summary and recommendations — everything else is deterministic assembly.
"""

import json
import re
import time
from datetime import datetime, timezone
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import PipelineState
from schemas.contract import ContractReport, IdentifiedClause, RiskAssessment
from config import GROQ_API_KEY, GROQ_MODEL


def _extract_metadata(clauses: list[dict]) -> dict:
    """Pull document metadata from identified clauses."""
    meta: dict = {
        "document_name": "Unknown Contract",
        "parties": [],
        "agreement_date": None,
        "effective_date": None,
        "governing_law": None,
    }

    for cl in clauses:
        ct = cl.get("clause_type", "")
        text = cl.get("text_excerpt", "")

        if ct == "Document Name" and text:
            meta["document_name"] = text[:200]
        elif ct == "Parties" and text:
            meta["parties"].append(text[:300])
        elif ct == "Agreement Date" and text:
            meta["agreement_date"] = text[:100]
        elif ct == "Effective Date" and text:
            meta["effective_date"] = text[:100]
        elif ct == "Governing Law" and text:
            meta["governing_law"] = text[:200]

    return meta


def report_agent(state: PipelineState) -> dict:
    """Agent 4 entry-point: assemble the final ContractReport."""

    clauses = state.get("identified_clauses", [])
    risks = state.get("risk_assessments", [])
    overall_score = state.get("overall_risk_score", 1.0)
    page_count = state.get("page_count", 0)
    errors: list[str] = list(state.get("errors", []))

    # ── Deterministic assembly ──────────────────────────────────────────
    metadata = _extract_metadata(clauses)

    high_count = sum(1 for r in risks if r.get("risk_level") == "HIGH")
    medium_count = sum(1 for r in risks if r.get("risk_level") == "MEDIUM")
    low_count = sum(1 for r in risks if r.get("risk_level") == "LOW")

    # Build validated clause objects
    identified = []
    for cl in clauses:
        try:
            identified.append(IdentifiedClause(
                clause_type=cl["clause_type"],
                text_excerpt=cl["text_excerpt"],
                page_number=cl.get("page_number", 1),
                section=cl.get("section", ""),
                confidence=cl.get("confidence", 0.8),
            ))
        except Exception:
            pass

    # Build validated risk objects
    assessed = []
    for r in risks:
        try:
            assessed.append(RiskAssessment(
                clause_type=r["clause_type"],
                risk_level=r["risk_level"],
                risk_score=r["risk_score"],
                risk_rationale=r["risk_rationale"],
                negotiation_tip=r["negotiation_tip"],
                source_text=r.get("source_text", ""),
            ))
        except Exception:
            pass

    # ── LLM-generated summary & recommendations ────────────────────────
    executive_summary = ""
    recommendations: list[str] = []
    risk_summary = ""

    if risks:
        # Reduced max_tokens to 1024 to save pre-request check TPM quota
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=1024,
        )

        # Build a concise risk digest for the LLM
        risk_digest = []
        for r in risks:
            if r.get("risk_score", 0) >= 5:
                risk_digest.append(
                    f"- {r['clause_type']} (score {r['risk_score']}/10): {r.get('risk_rationale', '')[:150]}"
                )

        system = """You are a senior legal advisor writing a concise executive summary for a contract review report.
Based on the risk findings provided, write:
1. "executive_summary": A highly concise, 1-2 sentence professional summary of the contract's risk profile. Focus only on the most critical exposures.
2. "risk_summary": A single-sentence verdict (e.g., "Moderate risk with 3 high-risk clauses requiring negotiation.").
3. "recommendations": A JSON list of 2-3 key, highly actionable next steps.

Return ONLY valid JSON:
{
    "executive_summary": "...",
    "risk_summary": "...",
    "recommendations": ["...", "..."]
}"""

        user = f"""Contract: {metadata['document_name']}
Overall Risk Score: {overall_score}/10
High-Risk Clauses: {high_count}, Medium: {medium_count}, Low: {low_count}
Total Clauses Found: {len(clauses)}

Key Risk Findings:
{chr(10).join(risk_digest) if risk_digest else 'No significant risks identified.'}

Generate the executive summary, risk summary, and recommendations."""

        max_retries = 3
        backoff = 15.0
        success = False

        for attempt in range(max_retries):
            try:
                # Sleep briefly to throttle calls
                time.sleep(2.0)

                response = llm.invoke([
                    SystemMessage(content=system),
                    HumanMessage(content=user),
                ])

                text = response.content.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                text = text.strip()

                # Robust extraction: find the JSON object in the text
                object_match = re.search(r"\{\s*\".*\}\s*", text, re.DOTALL)
                if object_match:
                    text = object_match.group(0)

                parsed = json.loads(text)
                executive_summary = parsed.get("executive_summary", "")
                risk_summary = parsed.get("risk_summary", "")
                recommendations = parsed.get("recommendations", [])
                success = True
                break

            except Exception as exc:
                exc_str = str(exc).lower()
                if any(k in exc_str for k in ["rate_limit", "rate limit", "tpm", "rpm", "413", "429", "too large"]):
                    print(f"  [Report Generator] Rate limit hit. Retrying in {backoff}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    print(f"\n[ERROR - Report Generator Agent] LLM invocation or parsing failed: {exc}")
                    errors.append(f"Summary generation error: {exc}")
                    executive_summary = f"Contract analysis complete. Overall risk score: {overall_score}/10 with {high_count} high-risk clauses identified."
                    risk_summary = f"Risk score {overall_score}/10 — {'HIGH' if overall_score >= 7 else 'MODERATE' if overall_score >= 4 else 'LOW'} risk."
                    recommendations = ["Review all high-risk clauses with legal counsel before signing."]
                    break

        if not success and attempt == max_retries - 1:
            errors.append(f"Summary generation failed after {max_retries} retries due to rate limits.")
            executive_summary = f"Contract analysis complete. Overall risk score: {overall_score}/10 with {high_count} high-risk clauses identified."
            risk_summary = f"Risk score {overall_score}/10 — {'HIGH' if overall_score >= 7 else 'MODERATE' if overall_score >= 4 else 'LOW'} risk."
            recommendations = ["Review all high-risk clauses with legal counsel before signing."]

    else:
        executive_summary = "No clauses were identified in this document for risk assessment."
        risk_summary = "Unable to assess risk — no clauses found."
        recommendations = ["Ensure the uploaded document is a valid legal contract."]

    # ── Assemble final report ───────────────────────────────────────────
    report = ContractReport(
        document_name=metadata["document_name"],
        parties=metadata["parties"],
        agreement_date=metadata["agreement_date"],
        effective_date=metadata["effective_date"],
        governing_law=metadata["governing_law"],
        overall_risk_score=overall_score,
        risk_summary=risk_summary,
        total_clauses_found=len(identified),
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        identified_clauses=identified,
        risk_assessments=assessed,
        executive_summary=executive_summary,
        recommendations=recommendations,
        analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        page_count=page_count,
    )

    report_dict = report.model_dump()

    print(f"  [Report Generator] Final report assembled — {len(identified)} clauses, score {overall_score}/10")

    return {
        "final_report": report_dict,
        "status": "complete",
        "errors": errors,
    }
