import json
import re
import time
from agents.state import PipelineState
from database.connection import SessionLocal
from database.models import ClauseType
from config import call_llm

# Retrieve risk category for clause type
def _get_risk_category(clause_type: str) -> str:
    db = SessionLocal()
    try:
        ct = db.query(ClauseType).filter(ClauseType.name == clause_type).first()
        return ct.risk_category if ct else "MEDIUM"
    finally:
        db.close()

# Prepare analysis instructions and schema
def _build_prompt(clause_type: str, text_excerpt: str, risk_cat: str) -> tuple[str, str]:
    system = """You are a legal risk analyst.
Analyze a legal clause and output a JSON object indicating the risk score, risk level, rationale, and a negotiation tip.

=== CRITICAL RULES ===
1. Risk score must be an integer between 1 and 10.
2. Return ONLY a valid JSON object. Do not include markdown tags or extra text.

=== OUTPUT FORMAT ===
{
  "risk_score": <int 1-10>,
  "risk_level": "<LOW / MEDIUM / HIGH>",
  "risk_rationale": "<why is this clause risky for the party receiving the contract>",
  "negotiation_tip": "<actionable advice to balance this clause>"
}"""

    user = f"""Clause Type: {clause_type} (Default Severity: {risk_cat})
Excerpt Text:
\"\"\"
{text_excerpt}
\"\"\"

Analyze this clause and return the JSON object."""
    return system, user

# Perform risk analysis on detected clauses
def risk_agent(state: PipelineState) -> dict:
    if state.get("status") in ["parse_error", "classification_error"]:
        return {"risk_assessments": [], "overall_risk_score": 0.0, "status": "risk_analysis_error"}

    clauses = state.get("identified_clauses", [])
    errors: list[str] = list(state.get("errors", []))

    if not clauses:
        print("  [Risk Analyzer] No clauses to analyze")
        return {
            "risk_assessments": [],
            "overall_risk_score": 0.0,
            "status": "analyzed_risks",
            "errors": errors,
        }

    print(f"  [Risk Analyzer] Analyzing risks for {len(clauses)} clauses...")
    assessments: list[dict] = []

    for idx, cl in enumerate(clauses):
        ctype = cl.get("clause_type", "Unknown")
        excerpt = cl.get("text_excerpt", "")
        pnum = cl.get("page_number", 1)

        if not excerpt:
            continue

        risk_cat = _get_risk_category(ctype)
        system_prompt, user_prompt = _build_prompt(ctype, excerpt, risk_cat)

        max_retries = 3
        backoff = 2.0
        success = False

        # Query LLM with retry loop
        for attempt in range(max_retries):
            try:
                time.sleep(1.0)
                response_text = call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.1,
                    max_tokens=1000
                )

                text = response_text.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                text = text.strip()

                obj_match = re.search(r"\{.*\}", text, re.DOTALL)
                if obj_match:
                    text = obj_match.group(0)

                parsed = json.loads(text)

                assessments.append({
                    "clause_type": ctype,
                    "source_text": excerpt,
                    "page_number": pnum,
                    "risk_score": int(parsed.get("risk_score", 5)),
                    "risk_level": parsed.get("risk_level", "MEDIUM").upper(),
                    "risk_rationale": parsed.get("risk_rationale", ""),
                    "negotiation_tip": parsed.get("negotiation_tip", ""),
                })
                success = True
                break

            except Exception as exc:
                print(f"  [Risk Analyzer] Attempt {attempt+1} failed for {ctype}: {exc}")
                time.sleep(backoff)
                backoff *= 2.0

        # Handle fallback in case of continuous failures
        if not success:
            fallback_score = 7 if risk_cat == "HIGH" else 4 if risk_cat == "MEDIUM" else 2
            assessments.append({
                "clause_type": ctype,
                "source_text": excerpt,
                "page_number": pnum,
                "risk_score": fallback_score,
                "risk_level": risk_cat,
                "risk_rationale": "High-risk category clause. Automated parsing timed out.",
                "negotiation_tip": "Review carefully with legal counsel.",
            })

    # Calculate overall risk score
    overall_score = 0.0
    if assessments:
        total_score = sum(r["risk_score"] for r in assessments)
        overall_score = total_score / len(assessments)

    print(f"  [Risk Analyzer] Risk analysis complete. Overall score: {overall_score:.2f}")

    return {
        "risk_assessments": assessments,
        "overall_risk_score": round(overall_score, 2),
        "status": "analyzed_risks",
        "errors": errors,
    }
