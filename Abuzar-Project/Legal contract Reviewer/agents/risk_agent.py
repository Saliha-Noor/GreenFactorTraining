"""Agent 3 — The Risk Analyzer: Evaluates identified clauses for risk and assigns scores.

Each risk score is backed by:
  • A predefined base-risk category per clause type (from CUAD)
  • LLM evaluation of the specific language
  • Every score references the exact source text
"""

import json
import re
import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import PipelineState
from config import GROQ_API_KEY, GROQ_MODEL

# Predefined base-risk weights per clause type (grounded in legal practice)
BASE_RISK: dict[str, dict] = {
    "Document Name":                       {"base": 1, "category": "LOW"},
    "Parties":                             {"base": 1, "category": "LOW"},
    "Agreement Date":                      {"base": 1, "category": "LOW"},
    "Effective Date":                      {"base": 1, "category": "LOW"},
    "Expiration Date":                     {"base": 3, "category": "MEDIUM"},
    "Renewal Term":                        {"base": 4, "category": "MEDIUM"},
    "Notice Period To Terminate Renewal":  {"base": 5, "category": "MEDIUM"},
    "Governing Law":                       {"base": 4, "category": "MEDIUM"},
    "Most Favored Nation":                 {"base": 5, "category": "MEDIUM"},
    "Non-Compete":                         {"base": 8, "category": "HIGH"},
    "Exclusivity":                         {"base": 7, "category": "HIGH"},
    "No-Solicit Of Customers":             {"base": 7, "category": "HIGH"},
    "Competitive Restriction Exception":   {"base": 4, "category": "MEDIUM"},
    "No-Solicit Of Employees":             {"base": 7, "category": "HIGH"},
    "Non-Disparagement":                   {"base": 4, "category": "MEDIUM"},
    "Termination For Convenience":         {"base": 7, "category": "HIGH"},
    "Rofr/Rofo/Rofn":                      {"base": 5, "category": "MEDIUM"},
    "Change Of Control":                   {"base": 7, "category": "HIGH"},
    "Anti-Assignment":                     {"base": 5, "category": "MEDIUM"},
    "Revenue/Profit Sharing":              {"base": 5, "category": "MEDIUM"},
    "Price Restrictions":                  {"base": 5, "category": "MEDIUM"},
    "Minimum Commitment":                  {"base": 7, "category": "HIGH"},
    "Volume Restriction":                  {"base": 5, "category": "MEDIUM"},
    "Ip Ownership Assignment":             {"base": 8, "category": "HIGH"},
    "Joint Ip Ownership":                  {"base": 7, "category": "HIGH"},
    "License Grant":                       {"base": 5, "category": "MEDIUM"},
    "Non-Transferable License":            {"base": 3, "category": "LOW"},
    "Affiliate License-Licensor":          {"base": 4, "category": "MEDIUM"},
    "Affiliate License-Licensee":          {"base": 4, "category": "MEDIUM"},
    "Unlimited/All-You-Can-Eat-License":   {"base": 5, "category": "MEDIUM"},
    "Irrevocable Or Perpetual License":    {"base": 8, "category": "HIGH"},
    "Source Code Escrow":                  {"base": 4, "category": "MEDIUM"},
    "Post-Termination Services":           {"base": 5, "category": "MEDIUM"},
    "Audit Rights":                        {"base": 4, "category": "MEDIUM"},
    "Uncapped Liability":                  {"base": 9, "category": "HIGH"},
    "Cap On Liability":                    {"base": 5, "category": "MEDIUM"},
    "Liquidated Damages":                  {"base": 8, "category": "HIGH"},
    "Warranty Duration":                   {"base": 4, "category": "MEDIUM"},
    "Insurance":                           {"base": 4, "category": "MEDIUM"},
    "Covenant Not To Sue":                 {"base": 8, "category": "HIGH"},
    "Third Party Beneficiary":             {"base": 5, "category": "MEDIUM"},
}


def risk_agent(state: PipelineState) -> dict:
    """Agent 3 entry-point: evaluate risk for every identified clause."""

    clauses = state.get("identified_clauses", [])
    errors: list[str] = list(state.get("errors", []))

    if not clauses:
        return {
            "risk_assessments": [],
            "overall_risk_score": 1.0,
            "status": "risk_analyzed",
            "errors": errors,
        }

    # Reduced max_tokens to 2048 to stay within Groq TPM limit checks
    llm = ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.15,
        max_tokens=2048,
    )

    # Build a compact clause summary for the LLM
    clause_summaries = []
    for idx, cl in enumerate(clauses):
        clause_summaries.append({
            "index": idx,
            "clause_type": cl["clause_type"],
            "text_excerpt": cl["text_excerpt"][:500],
            "page": cl.get("page_number", 0),
            "base_risk": BASE_RISK.get(cl["clause_type"], {}).get("category", "MEDIUM"),
        })

    system_prompt = """You are a legal risk assessment specialist. You will be given a list of identified contract clauses.
For EACH clause, you must:
1. Assess how risky the SPECIFIC LANGUAGE is (not just the clause type in general).
2. Assign a risk_score from 1 (completely safe) to 10 (extremely dangerous).
3. Provide a clear, concise risk_rationale explaining WHY.
4. Provide an actionable negotiation_tip for how to improve or push back on the clause.

RULES:
- Your assessment must be based on the ACTUAL TEXT provided, not generic advice.
- Consider one-sided terms, vague language, missing protections, overly broad scope.
- LOW base_risk clauses (Document Name, Parties, etc.) should generally score 1-3 unless the language itself is problematic.
- HIGH base_risk clauses need careful evaluation — they CAN score low if the language is fair and balanced.

Return ONLY a valid JSON array where each element is:
{
    "index": <matching index from input>,
    "clause_type": "<clause type>",
    "risk_level": "HIGH" or "MEDIUM" or "LOW",
    "risk_score": <1-10>,
    "risk_rationale": "<specific explanation>",
    "negotiation_tip": "<actionable suggestion>"
}"""

    user_prompt = f"""Analyze these contract clauses and assess risk for each one:

{json.dumps(clause_summaries, indent=2)}

Return ONLY the JSON array."""

    risk_assessments: list[dict] = []

    # Retry loop with exponential backoff for rate limits
    max_retries = 3
    backoff = 15.0
    success = False

    for attempt in range(max_retries):
        try:
            # Short sleep before invocation to stagger calls
            time.sleep(2.0)

            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])

            text = response.content.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = text.strip()

            # Robust extraction: find the JSON array in the text
            array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
            if array_match:
                text = array_match.group(0)

            parsed = json.loads(text)

            if isinstance(parsed, list):
                for item in parsed:
                    idx = item.get("index", -1)
                    if 0 <= idx < len(clauses):
                        source_clause = clauses[idx]
                        risk_assessments.append({
                            "clause_type": item.get("clause_type", source_clause["clause_type"]),
                            "risk_level": item.get("risk_level", "MEDIUM"),
                            "risk_score": max(1, min(10, int(item.get("risk_score", 5)))),
                            "risk_rationale": item.get("risk_rationale", ""),
                            "negotiation_tip": item.get("negotiation_tip", ""),
                            "source_text": source_clause.get("text_excerpt", ""),
                        })
                success = True
                break

        except Exception as exc:
            exc_str = str(exc).lower()
            if any(k in exc_str for k in ["rate_limit", "rate limit", "tpm", "rpm", "413", "429", "too large"]):
                print(f"  [Risk Analyzer] Rate limit hit. Retrying in {backoff}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2.0
            else:
                print(f"\n[ERROR - Risk Analyzer Agent] LLM invocation or parsing failed: {exc}")
                errors.append(f"Risk analysis error: {exc}")
                break

    if not success and attempt == max_retries - 1:
        errors.append(f"Risk analysis failed after {max_retries} retries due to rate limits.")

    # If LLM failed, generate rule-based fallback assessments
    if not risk_assessments:
        for cl in clauses:
            info = BASE_RISK.get(cl["clause_type"], {"base": 5, "category": "MEDIUM"})
            risk_assessments.append({
                "clause_type": cl["clause_type"],
                "risk_level": info["category"],
                "risk_score": info["base"],
                "risk_rationale": f"Base risk for {cl['clause_type']} clause type.",
                "negotiation_tip": "Review this clause carefully with legal counsel.",
                "source_text": cl.get("text_excerpt", ""),
            })

    # Calculate overall risk score
    if risk_assessments:
        scores = [r["risk_score"] for r in risk_assessments]
        # Weighted: high-risk clauses count more
        high_scores = [s for r, s in zip(risk_assessments, scores) if r["risk_level"] == "HIGH"]
        if high_scores:
            overall = round((sum(scores) / len(scores)) * 0.4 + (max(scores)) * 0.3 + (sum(high_scores) / len(high_scores)) * 0.3, 1)
        else:
            overall = round(sum(scores) / len(scores), 1)
        overall = max(1.0, min(10.0, overall))
    else:
        overall = 1.0

    print(f"  [Risk Analyzer] Assessed {len(risk_assessments)} clauses → overall score: {overall}/10")

    return {
        "risk_assessments": risk_assessments,
        "overall_risk_score": overall,
        "status": "risk_analyzed",
        "errors": errors,
    }
