import json
import re
import time
from datetime import datetime, timezone
from agents.state import PipelineState
from config import call_llm

# Build prompt for summarization and meta-extraction
def _build_prompt(state_dict: dict) -> tuple[str, str]:
    meta_info = {
        "file_path": state_dict.get("file_path", ""),
        "page_count": state_dict.get("page_count", 0),
        "overall_risk_score": state_dict.get("overall_risk_score", 0.0),
        "identified_clauses_count": len(state_dict.get("identified_clauses", [])),
    }

    risks_subset = []
    for r in state_dict.get("risk_assessments", []):
        risks_subset.append({
            "clause_type": r.get("clause_type"),
            "risk_score": r.get("risk_score"),
            "risk_level": r.get("risk_level"),
            "risk_rationale": r.get("risk_rationale", "")[:200],
        })

    system = """You are a legal contract report generator.
Synthesize the provided contract review metadata and risk assessments into a JSON report summary.

=== CRITICAL RULES ===
1. Return ONLY a valid JSON object. Do not include markdown tags or extra text.
2. The summary must be professional and objective.

=== OUTPUT FORMAT ===
{
  "document_name": "<formal title of contract or derived filename>",
  "parties": ["<party 1>", "<party 2>"],
  "agreement_date": "<date in YYYY-MM-DD or empty>",
  "governing_law": "<state / jurisdiction or empty>",
  "executive_summary": "<2-3 paragraph summary of the agreement, key risks, and overall legal exposure>",
  "risk_summary": "<1-2 sentence high-level risk summary sentence>",
  "recommendations": [
    "<actionable mitigation recommendation 1>",
    "<actionable mitigation recommendation 2>"
  ]
}"""

    user = f"""Contract Metadata:
{json.dumps(meta_info, indent=2)}

Risk Assessments:
{json.dumps(risks_subset, indent=2)}

Synthesize these inputs into the requested JSON report."""
    return system, user

# Compile and format the final evaluation report
def report_agent(state: PipelineState) -> dict:
    if state.get("status") in ["parse_error", "classification_error", "risk_analysis_error", "missing_clause_error", "conflict_detection_error"]:
        return {"final_report": {}, "status": "report_generation_error"}

    errors: list[str] = list(state.get("errors", []))
    filename = state.get("file_path", "contract.pdf").split("/")[-1].split("\\")[-1]

    system_prompt, user_prompt = _build_prompt(state)

    max_retries = 3
    backoff = 2.0
    parsed_report = {}
    success = False

    # Execute LLM querying loop with retries
    for attempt in range(max_retries):
        try:
            time.sleep(3.0)
            response_text = call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2048
            )

            text = response_text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = text.strip()

            obj_match = re.search(r"\{.*\}", text, re.DOTALL)
            if obj_match:
                text = obj_match.group(0)

            # Sanitize control characters that Groq sometimes injects
            text = re.sub(r'[\x00-\x1f\x7f](?<!")', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', text)

            parsed_report = json.loads(text, strict=False)
            success = True
            break

        except Exception as exc:
            print(f"  [Report Generator] Attempt {attempt+1} failed: {exc}")
            time.sleep(backoff)
            backoff *= 2.0

    # Apply fallback content in case of errors
    if not success:
        errors.append("Failed to generate synthesized report from LLM. Using fallback values.")
        parsed_report = {
            "document_name": filename,
            "parties": [],
            "agreement_date": "",
            "governing_law": "",
            "executive_summary": "Analysis completed. Individual risk assessments are available below.",
            "risk_summary": "Overall risk classification was determined from identified clauses.",
            "recommendations": ["Ensure manual review of all high-risk items."],
        }

    # Count risk levels in findings
    high_count = sum(1 for r in state.get("risk_assessments", []) if r["risk_score"] >= 7)
    med_count = sum(1 for r in state.get("risk_assessments", []) if 4 <= r["risk_score"] < 7)
    low_count = sum(1 for r in state.get("risk_assessments", []) if r["risk_score"] < 4)

    parsed_report["document_name"] = parsed_report.get("document_name") or filename
    parsed_report["page_count"] = state.get("page_count", 0)
    parsed_report["overall_risk_score"] = state.get("overall_risk_score", 0.0)
    parsed_report["high_risk_count"] = high_count
    parsed_report["medium_risk_count"] = med_count
    parsed_report["low_risk_count"] = low_count
    parsed_report["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()
    parsed_report["identified_clauses"] = state.get("identified_clauses", [])
    parsed_report["risk_assessments"] = state.get("risk_assessments", [])
    parsed_report["total_clauses_found"] = len(state.get("identified_clauses", []))
    parsed_report["contract_type"] = state.get("contract_type", "Unknown")
    parsed_report["missing_clause_analysis"] = state.get("missing_clause_analysis", [])
    parsed_report["completeness_score"] = state.get("completeness_score", 0.0)
    parsed_report["conflict_analysis"] = state.get("conflict_analysis", [])
    parsed_report["consistency_score"] = state.get("consistency_score", 100.0)
    parsed_report["consistency_explanation"] = state.get("consistency_explanation", "")

    print(f"  [Report Generator] Compiled report for {filename}")

    return {
        "final_report": parsed_report,
        "status": "complete",
        "errors": errors,
    }
