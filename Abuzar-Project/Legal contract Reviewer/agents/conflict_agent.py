import json
import re
import time
from typing import List, Dict, Any
from agents.state import PipelineState
from config import call_llm

class ConflictClassifier:
    """Normalizes clause texts and groups them into specific conflict categories."""
    
    def normalize_text(self, text: str) -> str:
        # Standardize whitespace and casing for comparison
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def group_clauses(self, clauses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        categories = {
            "Payment": [],
            "Date": [],
            "Termination": [],
            "Renewal": [],
            "Confidentiality": [],
            "Liability": [],
            "Governing Law": [],
            "Arbitration": [],
            "Responsibility": [],
            "Duplicate Clauses": []
        }

        for idx, cl in enumerate(clauses):
            cl_copy = dict(cl)
            cl_copy["clause_number"] = idx + 1  # Assign a sequential number for tracing
            
            ctype = cl.get("clause_type", "")
            text = cl.get("text_excerpt", "")
            text_lower = text.lower()
            
            matched = False
            
            # 1. Payment Conflicts
            if ctype in ["Revenue/Profit Sharing", "Price Restrictions", "Minimum Commitment"] or \
               any(k in text_lower for k in ["payment", "invoice", "late fee", "due within", "remit", "pricing"]):
                categories["Payment"].append(cl_copy)
                matched = True
                
            # 2. Date Conflicts
            if ctype in ["Effective Date", "Expiration Date"] or \
               any(k in text_lower for k in ["commencement date", "starts on", "begins on", "effective as of"]):
                categories["Date"].append(cl_copy)
                matched = True
                
            # 3. Termination Conflicts
            if ctype in ["Termination For Convenience", "Post-Termination Services"] or \
               any(k in text_lower for k in ["terminate", "termination", "cancel at any time", "termination notice"]):
                categories["Termination"].append(cl_copy)
                matched = True
                
            # 4. Renewal Conflicts
            if ctype in ["Renewal Term", "Notice Period To Terminate Renewal"] or \
               any(k in text_lower for k in ["renew", "automatic renewal", "auto-renew", "renewal period"]):
                categories["Renewal"].append(cl_copy)
                matched = True
                
            # 5. Confidentiality Conflicts
            if any(k in text_lower for k in ["confidential", "non-disclosure", "disclose", "share information", "third parties"]):
                categories["Confidentiality"].append(cl_copy)
                matched = True
                
            # 6. Liability Conflicts
            if ctype in ["Cap On Liability", "Uncapped Liability", "Liquidated Damages"] or \
               any(k in text_lower for k in ["liability cap", "uncapped", "limitation of liability", "indemnification cap"]):
                categories["Liability"].append(cl_copy)
                matched = True
                
            # 7. Governing Law Conflicts
            if ctype == "Governing Law" or \
               any(k in text_lower for k in ["governing law", "governed by", "applicable law"]):
                categories["Governing Law"].append(cl_copy)
                matched = True
                
            # 8. Arbitration Conflicts
            if ctype == "Covenant Not To Sue" or \
               any(k in text_lower for k in ["arbitration", "arbitrate", "dispute resolution", "resolved in court", "jurisdiction of the courts"]):
                categories["Arbitration"].append(cl_copy)
                matched = True
                
            # 9. Responsibility Conflicts
            if ctype in ["Ip Ownership Assignment", "Joint Ip Ownership", "License Grant", "Non-Transferable License"] or \
               any(k in text_lower for k in ["responsible for", "obligation of", "maintenance by", "duties of"]):
                categories["Responsibility"].append(cl_copy)
                matched = True

            # 10. Check for Duplicates (all clauses are grouped here to compare later)
            categories["Duplicate Clauses"].append(cl_copy)

        return categories


class ConflictComparator:
    """Compares clauses within categories to identify contradictions using rules and LLM reasoning."""

    def compare_group(self, category: str, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(clauses) < 2:
            return []

        # Construct safe list for LLM analysis
        clauses_input = [
            {
                "clause_number": cl["clause_number"],
                "clause_type": cl.get("clause_type", "Unknown"),
                "page_number": cl.get("page_number", 1),
                "text_excerpt": cl.get("text_excerpt", "")
            }
            for cl in clauses
        ]

        system_prompt = """You are an expert legal contract consistency analyst.
Your job is to detect logical inconsistencies, contradictory clauses, conflicting obligations, duplicated conditions, and ambiguous provisions.

Compare the provided clauses against one another. You must determine if any clauses cannot logically coexist (e.g. different timelines, conflicting obligations, contradictory locations/percentages/laws).

=== CRITICAL RULES ===
1. Return ONLY a valid JSON array. Do not include markdown tags, code block wraps (like ```json), or extra text.
2. If no conflicts or contradictions are found, return an empty JSON array: []
3. Each detected conflict object must contain:
   - conflict_id: string (e.g. "CONF-001")
   - clause_numbers: list of integers (the clause numbers that conflict)
   - original_clauses: list of strings (the exact excerpts that contradict)
   - conflict_category: string (exactly the category name being analyzed)
   - severity: string ("Low", "Medium", "High", "Critical")
   - why_conflict: string (clear explanation in plain English)
   - stronger_clause: string (detailed explanation of which clause is likely stronger legally and why)
   - consequences: string (potential legal consequences, e.g. "May create litigation", "Causes ambiguity", "Contract unenforceability")
   - harmonized_clause: string (a legally balanced replacement that resolves the contradiction)
   - confidence_score: integer (0-100 percentage)"""

        user_prompt = f"""Conflict Category: {category}

Clauses to analyze:
{json.dumps(clauses_input, indent=2)}

Analyze these clauses and return a JSON array containing any detected contradictions or conflicts. If none exist, return []."""

        max_retries = 3
        backoff = 2.0

        for attempt in range(max_retries):
            try:
                time.sleep(3.0)
                response = call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.1,
                    max_tokens=2548
                )
                
                text = response.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                text = text.strip()

                array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
                if array_match:
                    text = array_match.group(0)

                # Clean control characters
                text = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', text)

                parsed = json.loads(text, strict=False)
                if isinstance(parsed, list):
                    return parsed
                return []
            except Exception as e:
                print(f"  [Conflict Detector] Group {category} comparison attempt {attempt+1} failed: {e}")
                time.sleep(backoff)
                backoff *= 2.0

        return []


class ConsistencyScorer:
    """Calculates overall Contract Consistency Score and generates the explanation."""
    
    def calculate_score(self, conflicts: List[Dict[str, Any]]) -> tuple[float, str]:
        if not conflicts:
            return 100.0, "Perfect consistency. No conflicting obligations, contradictions, or duplicates were detected."

        score = 100.0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for c in conflicts:
            sev = c.get("severity", "Medium").upper()
            if "CRITICAL" in sev:
                score -= 25
                critical_count += 1
            elif "HIGH" in sev:
                score -= 15
                high_count += 1
            elif "MEDIUM" in sev:
                score -= 10
                medium_count += 1
            else:
                score -= 5
                low_count += 1

        # Bound score between 10 and 100
        score = max(10.0, score)

        # Build explanation
        deductions = []
        if critical_count > 0:
            deductions.append(f"{critical_count} Critical conflict(s) (-{critical_count * 25} pts)")
        if high_count > 0:
            deductions.append(f"{high_count} High conflict(s) (-{high_count * 15} pts)")
        if medium_count > 0:
            deductions.append(f"{medium_count} Medium conflict(s) (-{medium_count * 10} pts)")
        if low_count > 0:
            deductions.append(f"{low_count} Low conflict(s) (-{low_count * 5} pts)")

        explanation = f"Consistency score calculated starting from a base of 100. Deducted for: {', '.join(deductions)}."
        
        # Add summary statement
        if score >= 90:
            explanation += " Overall, the contract maintains high logical consistency."
        elif score >= 70:
            explanation += " The contract contains minor conflicts that create ambiguity but do not invalidate major covenants."
        elif score >= 50:
            explanation += " Moderate contradictions exist. Crucial terms regarding dates, payments, or liabilities conflict and need resolution."
        else:
            explanation += " Highly contradictory obligations detected. These conflicts pose significant risks of unenforceability or litigation."

        return round(score, 1), explanation


class ConflictReportGenerator:
    """Generates visual text output and updates report dictionary."""

    def format_summary(self, conflicts: List[Dict[str, Any]], score: float) -> str:
        output = []
        output.append("================================")
        output.append("Contract Consistency Report")
        output.append(f"Overall Score: {score}/100")
        output.append(f"Conflicts Found: {len(conflicts)}")
        
        high_count = sum(1 for c in conflicts if c.get("severity", "").upper() == "HIGH")
        critical_count = sum(1 for c in conflicts if c.get("severity", "").upper() == "CRITICAL")
        med_count = sum(1 for c in conflicts if c.get("severity", "").upper() == "MEDIUM")
        low_count = sum(1 for c in conflicts if c.get("severity", "").upper() == "LOW")

        output.append(f"Critical: {critical_count}")
        output.append(f"High: {high_count}")
        output.append(f"Medium: {med_count}")
        output.append(f"Low: {low_count}")
        output.append("================================")

        for idx, c in enumerate(conflicts, 1):
            clauses_str = ", ".join(f"Clause {n}" for n in c.get("clause_numbers", []))
            output.append(f"Conflict {idx}")
            output.append(f"Category: {c.get('conflict_category', 'General')}")
            output.append(f"Severity: {c.get('severity', 'Medium')}")
            output.append(f"Clauses involved: {clauses_str}")
            output.append(f"Reason: {c.get('why_conflict', '')}")
            output.append(f"Suggested Resolution: {c.get('harmonized_clause', '')}")
            output.append("--------------------------------")

        return "\n".join(output)


def conflict_agent(state: PipelineState) -> dict:
    """Executes conflict detection across extracted clauses and updates the pipeline state."""
    
    if state.get("status") in ["parse_error", "classification_error", "risk_analysis_error", "missing_clause_error"]:
        return {
            "conflict_analysis": [],
            "consistency_score": 100.0,
            "consistency_explanation": "Skipped due to upstream errors.",
            "status": "conflict_detection_error"
        }

    clauses = state.get("identified_clauses", [])
    errors = list(state.get("errors", []))

    if not clauses:
        print("  [Conflict Detector] No clauses extracted. Skipping consistency check.")
        return {
            "conflict_analysis": [],
            "consistency_score": 100.0,
            "consistency_explanation": "Perfect consistency score assigned as no clauses were extracted for comparison.",
            "status": "conflict_detection_complete",
            "errors": errors
        }

    print(f"  [Conflict Detector] Grouping and checking {len(clauses)} clauses for inconsistencies...")

    classifier = ConflictClassifier()
    comparator = ConflictComparator()
    scorer = ConsistencyScorer()
    report_gen = ConflictReportGenerator()

    # 1. Group clauses into conflict categories
    grouped = classifier.group_clauses(clauses)

    all_conflicts = []

    # 2. Compare clauses in each category
    for category, group_clauses in grouped.items():
        if len(group_clauses) < 2:
            continue
            
        print(f"  [Conflict Detector] Comparing {len(group_clauses)} clauses in '{category}' category...")
        conflicts = comparator.compare_group(category, group_clauses)
        if conflicts:
            print(f"  [Conflict Detector] Found {len(conflicts)} conflict(s) in category: {category}")
            all_conflicts.extend(conflicts)

    # 3. Score overall contract consistency
    consistency_score, score_explanation = scorer.calculate_score(all_conflicts)
    print(f"  [Conflict Detector] Consistency score: {consistency_score}/100. Conflicts: {len(all_conflicts)}")

    # 4. Generate console summary log
    console_summary = report_gen.format_summary(all_conflicts, consistency_score)
    print(console_summary)

    return {
        "conflict_analysis": all_conflicts,
        "consistency_score": consistency_score,
        "consistency_explanation": score_explanation,
        "status": "conflict_detection_complete",
        "errors": errors
    }
