import json
import re
import time
from agents.state import PipelineState
from config import call_llm

# Standard clauses expected per contract type
# Each key maps to a list of CUAD clause type names that are typically present
CONTRACT_TYPE_CLAUSES = {
    "NDA / Confidentiality Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Governing Law",
        "Non-Compete",
        "No-Solicit Of Employees",
        "No-Solicit Of Customers",
        "Non-Disparagement",
        "Termination For Convenience",
        "Anti-Assignment",
        "Covenant Not To Sue",
    ],
    "Employment Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Governing Law",
        "Non-Compete",
        "No-Solicit Of Employees",
        "No-Solicit Of Customers",
        "Non-Disparagement",
        "Termination For Convenience",
        "Ip Ownership Assignment",
        "Anti-Assignment",
        "Insurance",
        "Covenant Not To Sue",
    ],
    "Software / SaaS Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Notice Period To Terminate Renewal",
        "Governing Law",
        "License Grant",
        "Non-Transferable License",
        "Ip Ownership Assignment",
        "Cap On Liability",
        "Warranty Duration",
        "Termination For Convenience",
        "Anti-Assignment",
        "Audit Rights",
        "Source Code Escrow",
        "Post-Termination Services",
        "Insurance",
    ],
    "License Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Governing Law",
        "License Grant",
        "Non-Transferable License",
        "Affiliate License-Licensor",
        "Affiliate License-Licensee",
        "Unlimited/All-You-Can-Eat-License",
        "Irrevocable Or Perpetual License",
        "Ip Ownership Assignment",
        "Joint Ip Ownership",
        "Cap On Liability",
        "Warranty Duration",
        "Termination For Convenience",
        "Anti-Assignment",
        "Audit Rights",
    ],
    "Distribution / Supply Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Governing Law",
        "Exclusivity",
        "Most Favored Nation",
        "Minimum Commitment",
        "Volume Restriction",
        "Price Restrictions",
        "Revenue/Profit Sharing",
        "Non-Compete",
        "Termination For Convenience",
        "Anti-Assignment",
        "Cap On Liability",
        "Insurance",
        "Audit Rights",
    ],
    "Joint Venture / Partnership Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Governing Law",
        "Revenue/Profit Sharing",
        "Joint Ip Ownership",
        "Ip Ownership Assignment",
        "Non-Compete",
        "Exclusivity",
        "Change Of Control",
        "Anti-Assignment",
        "Termination For Convenience",
        "Cap On Liability",
        "Audit Rights",
        "Insurance",
        "Governing Law",
    ],
    "Merger / Acquisition Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Governing Law",
        "Change Of Control",
        "Non-Compete",
        "No-Solicit Of Employees",
        "No-Solicit Of Customers",
        "Anti-Assignment",
        "Ip Ownership Assignment",
        "Rofr/Rofo/Rofn",
        "Cap On Liability",
        "Uncapped Liability",
        "Liquidated Damages",
        "Termination For Convenience",
        "Third Party Beneficiary",
        "Insurance",
    ],
    "Service Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Governing Law",
        "Termination For Convenience",
        "Anti-Assignment",
        "Cap On Liability",
        "Warranty Duration",
        "Insurance",
        "Audit Rights",
        "Ip Ownership Assignment",
        "Non-Compete",
        "Post-Termination Services",
    ],
    "Endorsement / Sponsorship Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Governing Law",
        "Exclusivity",
        "Non-Compete",
        "Non-Disparagement",
        "License Grant",
        "Ip Ownership Assignment",
        "Termination For Convenience",
        "Anti-Assignment",
        "Cap On Liability",
        "Liquidated Damages",
    ],
    "Research / Development Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Governing Law",
        "Ip Ownership Assignment",
        "Joint Ip Ownership",
        "License Grant",
        "Non-Compete",
        "Exclusivity",
        "Revenue/Profit Sharing",
        "Termination For Convenience",
        "Anti-Assignment",
        "Cap On Liability",
        "Audit Rights",
        "Insurance",
    ],
    "Lease / Real Estate Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Notice Period To Terminate Renewal",
        "Governing Law",
        "Termination For Convenience",
        "Anti-Assignment",
        "Insurance",
        "Cap On Liability",
        "Audit Rights",
    ],
    "Franchise Agreement": [
        "Parties",
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Governing Law",
        "Exclusivity",
        "Non-Compete",
        "License Grant",
        "Non-Transferable License",
        "Revenue/Profit Sharing",
        "Minimum Commitment",
        "Termination For Convenience",
        "Anti-Assignment",
        "Audit Rights",
        "Insurance",
        "Cap On Liability",
    ],
}


# Detect contract type from classified clauses using heuristic matching and LLM fallback
def _detect_contract_type(identified_clauses: list[dict], raw_text: str) -> tuple[str, str]:
    found_types = set()
    for cl in identified_clauses:
        found_types.add(cl.get("clause_type", ""))

    # Score each contract type by overlap with found clauses
    best_type = "Service Agreement"
    best_score = 0

    for ctype, expected in CONTRACT_TYPE_CLAUSES.items():
        overlap = len(found_types.intersection(set(expected)))
        score = overlap / len(expected) if expected else 0
        if score > best_score:
            best_score = score
            best_type = ctype

    # If heuristic is weak, use LLM to classify from raw text
    if best_score < 0.15:
        try:
            contract_types_list = ", ".join(CONTRACT_TYPE_CLAUSES.keys())
            system = f"""You are a legal contract type classifier.
Given a contract excerpt, determine which type of agreement it is.

Choose EXACTLY ONE from this list:
{contract_types_list}

Return ONLY the contract type name, nothing else."""

            # Use first 3000 chars of raw text for classification
            excerpt = raw_text[:3000] if raw_text else ""
            user = f"""Contract excerpt:
\"\"\"
{excerpt}
\"\"\"

What type of agreement is this? Return ONLY the type name."""

            response = call_llm(system_prompt=system, user_prompt=user, temperature=0.1, max_tokens=100)
            detected = response.strip().strip('"').strip("'")

            # Validate against known types
            for known_type in CONTRACT_TYPE_CLAUSES:
                if known_type.lower() in detected.lower() or detected.lower() in known_type.lower():
                    best_type = known_type
                    break

        except Exception as exc:
            print(f"  [Missing Clause] LLM contract type detection failed: {exc}")

    method = "llm_fallback" if best_score < 0.15 else "heuristic"
    return best_type, method


# Categorize clauses into present, missing, and weakly defined
def _categorize_clauses(
    expected_clauses: list[str],
    identified_clauses: list[dict],
) -> tuple[list[str], list[str], list[dict]]:
    found_map: dict[str, float] = {}
    for cl in identified_clauses:
        ctype = cl.get("clause_type", "")
        confidence = cl.get("confidence", 0.0)
        # Keep highest confidence per clause type
        if ctype not in found_map or confidence > found_map[ctype]:
            found_map[ctype] = confidence

    present: list[str] = []
    missing: list[str] = []
    weakly_defined: list[dict] = []

    for expected in expected_clauses:
        if expected in found_map:
            if found_map[expected] < 0.5:
                weakly_defined.append({
                    "clause_type": expected,
                    "confidence": found_map[expected],
                })
            else:
                present.append(expected)
        else:
            missing.append(expected)

    return present, missing, weakly_defined


# Analyze a batch of missing clauses using the LLM
def _analyze_missing_clauses(
    clause_names: list[str],
    contract_type: str,
) -> list[dict]:
    if not clause_names:
        return []

    clause_list_str = "\n".join(f"  {i+1}. {name}" for i, name in enumerate(clause_names))

    system = """You are a legal contract analyst specializing in clause completeness review.
For each missing clause, provide a detailed analysis including its importance, the legal risks
caused by its absence, and generate a recommended clause that could be added to the contract.

=== CRITICAL RULES ===
1. Return ONLY a valid JSON array. Do not include markdown tags or extra text.
2. Each element must follow the exact output format below.
3. The recommended_clause should be professional legal language suitable for insertion.

=== OUTPUT FORMAT ===
[
  {
    "clause_type": "<exact clause name>",
    "importance": "<2-3 sentence explanation of why this clause matters>",
    "legal_risks": "<2-3 sentence description of risks caused by its absence>",
    "recommended_clause": "<professionally drafted clause text, 3-6 sentences>"
  }
]"""

    user = f"""Contract Type: {contract_type}

The following clauses are MISSING from this {contract_type}:
{clause_list_str}

For each missing clause, provide the importance, legal risks of absence, and a recommended
clause that should be added. Return ONLY the JSON array."""

    max_retries = 3
    backoff = 2.0

    for attempt in range(max_retries):
        try:
            time.sleep(3.0)
            response_text = call_llm(
                system_prompt=system,
                user_prompt=user,
                temperature=0.2,
                max_tokens=4000,
            )

            text = response_text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = text.strip()

            array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
            if array_match:
                text = array_match.group(0)

            # Sanitize control characters that Groq sometimes injects
            text = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', text)

            parsed = json.loads(text, strict=False)
            if isinstance(parsed, list):
                return parsed
            return []

        except Exception as exc:
            print(f"  [Missing Clause] Attempt {attempt+1} failed: {exc}")
            time.sleep(backoff)
            backoff *= 2.0

    # Return fallback entries if all attempts fail
    return [
        {
            "clause_type": name,
            "importance": "This clause is standard for this agreement type. Its absence may create legal gaps.",
            "legal_risks": "Without this clause, parties may face unaddressed legal exposure. Manual review recommended.",
            "recommended_clause": "A qualified legal professional should draft this clause based on the specific agreement context.",
        }
        for name in clause_names
    ]


# Analyze weakly defined clauses using the LLM
def _analyze_weak_clauses(
    weak_clauses: list[dict],
    contract_type: str,
) -> list[dict]:
    if not weak_clauses:
        return []

    clause_list_str = "\n".join(
        f"  {i+1}. {cl['clause_type']} (confidence: {cl['confidence']:.0%})"
        for i, cl in enumerate(weak_clauses)
    )

    system = """You are a legal contract analyst specializing in clause quality review.
For each weakly defined clause, explain why the existing language may be insufficient,
describe the legal risks of having a vague or poorly drafted clause, and provide a
strengthened recommended clause.

=== CRITICAL RULES ===
1. Return ONLY a valid JSON array. Do not include markdown tags or extra text.

=== OUTPUT FORMAT ===
[
  {
    "clause_type": "<exact clause name>",
    "importance": "<why a strong version of this clause matters>",
    "legal_risks": "<risks of the current weak/vague definition>",
    "recommended_clause": "<strengthened clause text, 3-6 sentences>"
  }
]"""

    user = f"""Contract Type: {contract_type}

The following clauses are WEAKLY DEFINED in this {contract_type} (low confidence indicates
vague or insufficient language):
{clause_list_str}

For each weakly defined clause, provide analysis and a strengthened version.
Return ONLY the JSON array."""

    max_retries = 3
    backoff = 2.0

    for attempt in range(max_retries):
        try:
            time.sleep(3.0)
            response_text = call_llm(
                system_prompt=system,
                user_prompt=user,
                temperature=0.2,
                max_tokens=3000,
            )

            text = response_text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = text.strip()

            array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
            if array_match:
                text = array_match.group(0)

            # Sanitize control characters that Groq sometimes injects
            text = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', text)

            parsed = json.loads(text, strict=False)
            if isinstance(parsed, list):
                return parsed
            return []

        except Exception as exc:
            print(f"  [Missing Clause] Weak clause analysis attempt {attempt+1} failed: {exc}")
            time.sleep(backoff)
            backoff *= 2.0

    return [
        {
            "clause_type": cl["clause_type"],
            "importance": "This clause exists but appears to be vaguely defined. Strengthening recommended.",
            "legal_risks": "Weak clause language may be unenforceable or lead to disputes over interpretation.",
            "recommended_clause": "A qualified legal professional should review and strengthen this clause.",
        }
        for cl in weak_clauses
    ]


# Main missing clause detection agent entry point
def missing_clause_agent(state: PipelineState) -> dict:
    if state.get("status") in ["parse_error", "classification_error", "risk_analysis_error"]:
        return {
            "contract_type": "Unknown",
            "missing_clause_analysis": [],
            "completeness_score": 0.0,
            "status": "missing_clause_error",
        }

    identified_clauses = state.get("identified_clauses", [])
    raw_text = state.get("raw_text", "")
    errors: list[str] = list(state.get("errors", []))

    if not identified_clauses:
        print("  [Missing Clause] No identified clauses to compare against")
        return {
            "contract_type": "Unknown",
            "missing_clause_analysis": [],
            "completeness_score": 0.0,
            "status": "missing_clause_complete",
            "errors": errors,
        }

    # Step 1: Detect contract type
    print("  [Missing Clause] Detecting contract type...")
    contract_type, method = _detect_contract_type(identified_clauses, raw_text)
    print(f"  [Missing Clause] Detected: {contract_type} (method: {method})")

    # Step 2: Get expected clauses for this contract type
    expected_clauses = CONTRACT_TYPE_CLAUSES.get(contract_type, [])
    if not expected_clauses:
        print(f"  [Missing Clause] No expected clauses defined for type: {contract_type}")
        return {
            "contract_type": contract_type,
            "missing_clause_analysis": [],
            "completeness_score": 100.0,
            "status": "missing_clause_complete",
            "errors": errors,
        }

    # Step 3: Categorize clauses
    present, missing, weakly_defined = _categorize_clauses(expected_clauses, identified_clauses)

    print(f"  [Missing Clause] Present: {len(present)}, Missing: {len(missing)}, Weakly Defined: {len(weakly_defined)}")

    # Step 4: Analyze missing clauses (batch in groups of 5)
    all_analysis: list[dict] = []

    if missing:
        print(f"  [Missing Clause] Analyzing {len(missing)} missing clauses...")
        for batch_start in range(0, len(missing), 5):
            batch = missing[batch_start : batch_start + 5]
            batch_results = _analyze_missing_clauses(batch, contract_type)
            for result in batch_results:
                result["status"] = "missing"
            all_analysis.extend(batch_results)

    # Step 5: Analyze weakly defined clauses
    if weakly_defined:
        print(f"  [Missing Clause] Analyzing {len(weakly_defined)} weakly defined clauses...")
        weak_results = _analyze_weak_clauses(weakly_defined, contract_type)
        for result in weak_results:
            result["status"] = "weakly_defined"
        all_analysis.extend(weak_results)

    # Step 6: Calculate completeness score
    total_expected = len(expected_clauses)
    present_count = len(present)
    weak_count = len(weakly_defined)
    completeness_score = round(
        ((present_count + 0.5 * weak_count) / total_expected) * 100, 1
    ) if total_expected > 0 else 100.0

    print(f"  [Missing Clause] Completeness score: {completeness_score}%")
    print(f"  [Missing Clause] Analysis complete. Generated {len(all_analysis)} clause analyses.")

    return {
        "contract_type": contract_type,
        "missing_clause_analysis": all_analysis,
        "completeness_score": completeness_score,
        "status": "missing_clause_complete",
        "errors": errors,
    }
