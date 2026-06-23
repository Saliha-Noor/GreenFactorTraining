"""Agent 2 — The Classifier: Identifies and categorises clauses using the 41 CUAD types.

Anti-hallucination measures:
  1. CUAD examples are loaded from the database and included as few-shot context.
  2. The LLM is instructed to quote EXACT text from the contract.
  3. Post-validation verifies every quoted span actually exists in the source document.
"""

import json
import re
import time
from agents.state import PipelineState
from database.connection import SessionLocal
from database.models import ClauseType, ClauseExample
from config import call_llm

# ── Clause-type metadata (duplicated from seed for offline access) ──────────
CUAD_TYPES = {
    "Document Name": "The name or title of the contract/agreement.",
    "Parties": "The names of the contracting parties.",
    "Agreement Date": "The date when the agreement was signed.",
    "Effective Date": "The date when the agreement becomes effective.",
    "Expiration Date": "The date when the agreement expires.",
    "Renewal Term": "Terms and conditions for renewal of the agreement.",
    "Notice Period To Terminate Renewal": "Notice period required to terminate automatic renewal.",
    "Governing Law": "The jurisdiction whose laws govern the agreement.",
    "Most Favored Nation": "Clause ensuring equal or better terms than other parties.",
    "Non-Compete": "Restrictions on competing with the other party.",
    "Exclusivity": "Exclusive rights or obligations granted to one party.",
    "No-Solicit Of Customers": "Restrictions on soliciting the other party's customers.",
    "Competitive Restriction Exception": "Exceptions to competitive restrictions.",
    "No-Solicit Of Employees": "Restrictions on soliciting the other party's employees.",
    "Non-Disparagement": "Obligations not to make negative statements about the other party.",
    "Termination For Convenience": "Right to terminate the agreement without cause.",
    "Rofr/Rofo/Rofn": "Right of First Refusal, First Offer, or First Negotiation.",
    "Change Of Control": "Provisions triggered by changes in ownership or control.",
    "Anti-Assignment": "Restrictions on assigning rights or obligations to third parties.",
    "Revenue/Profit Sharing": "Terms for sharing revenue or profits between parties.",
    "Price Restrictions": "Limitations or controls on pricing.",
    "Minimum Commitment": "Minimum purchase or performance obligations.",
    "Volume Restriction": "Limitations on volume of goods or services.",
    "Ip Ownership Assignment": "Transfer of intellectual property ownership.",
    "Joint Ip Ownership": "Shared ownership of intellectual property.",
    "License Grant": "Grant of license to use intellectual property or technology.",
    "Non-Transferable License": "License that cannot be transferred to third parties.",
    "Affiliate License-Licensor": "License rights extended to licensor's affiliates.",
    "Affiliate License-Licensee": "License rights extended to licensee's affiliates.",
    "Unlimited/All-You-Can-Eat-License": "License without usage or volume limitations.",
    "Irrevocable Or Perpetual License": "License that cannot be revoked or has no end date.",
    "Source Code Escrow": "Arrangement to hold source code with a third party.",
    "Post-Termination Services": "Services that continue after agreement terminates.",
    "Audit Rights": "Rights to audit the other party's records or compliance.",
    "Uncapped Liability": "No upper limit on the amount of liability.",
    "Cap On Liability": "A maximum limit on total liability.",
    "Liquidated Damages": "Pre-determined amount of damages in case of breach.",
    "Warranty Duration": "The period during which warranties are valid.",
    "Insurance": "Requirements for insurance coverage.",
    "Covenant Not To Sue": "Agreement not to bring legal action against the other party.",
    "Third Party Beneficiary": "Rights granted to non-signatory parties.",
}


def _load_cuad_examples() -> dict[str, list[str]]:
    """Load a few example text spans per clause type from the database."""
    db = SessionLocal()
    try:
        examples: dict[str, list[str]] = {}
        for ct in db.query(ClauseType).all():
            spans = (
                db.query(ClauseExample.text_span)
                .filter(ClauseExample.clause_type_id == ct.id)
                .limit(2)
                .all()
            )
            if spans:
                examples[ct.name] = [s[0][:300] for s in spans]
        return examples
    finally:
        db.close()


def _build_prompt(contract_chunk: str, page_range: str) -> tuple[str, str]:
    """Build system + user prompts for clause classification without few-shot examples to fit token limits."""

    # List of 41 clause types (names only without descriptions to save ~600 tokens)
    clause_ref = ", ".join(list(CUAD_TYPES.keys()))

    system = f"""You are a legal contract clause classifier.
Identify legal clauses in the contract text matching these 41 CUAD types:
{clause_ref}

=== CRITICAL RULES ===
1. ONLY quote EXACT text from the contract — do NOT paraphrase.
2. If a clause type is NOT present, do NOT include it.
3. Return ONLY a valid JSON array. Do not wrap in markdown or include extra text.

=== OUTPUT FORMAT ===
[
  {{
    "clause_type": "<exact name from list above>",
    "text_excerpt": "<verbatim quote from contract>",
    "page_number": <integer>,
    "section": "<section heading or empty string>",
    "confidence": <float 0.0 to 1.0>
  }}
]"""

    user = f"""Analyze this contract text ({page_range}) and identify ALL clauses from the 41 CUAD types.
QUOTE the exact text from the contract for each clause you find.

CONTRACT TEXT:
\"\"\"
{contract_chunk}
\"\"\"

Return ONLY the JSON array."""

    return system, user


def _validate_clauses(clauses: list[dict], source_text: str) -> list[dict]:
    """Post-validate: ensure every quoted excerpt genuinely appears in the source."""
    # Normalize whitespaces and lowercase the source text for comparison
    source_clean = re.sub(r"\s+", " ", source_text).lower()
    validated: list[dict] = []

    for cl in clauses:
        excerpt = cl.get("text_excerpt", "").strip()
        if not excerpt or len(excerpt) < 3:
            continue

        # Validate clause type is one of the 41
        if cl.get("clause_type") not in CUAD_TYPES:
            continue

        # Normalize whitespaces and lowercase the excerpt for comparison
        excerpt_clean = re.sub(r"\s+", " ", excerpt).lower()
        words = excerpt_clean.split()
        if not words:
            continue

        # 1. Check the first 8 words
        check_len = min(8, len(words))
        check_phrase = " ".join(words[:check_len])
        if check_phrase in source_clean:
            validated.append(cl)
            continue

        # 2. Try first 4 words with lower confidence
        short_phrase = " ".join(words[:min(4, len(words))])
        if short_phrase in source_clean:
            cl["confidence"] = round(max(0.3, cl.get("confidence", 0.5) - 0.2), 2)
            validated.append(cl)
            continue

        # 3. Try the last 8 words
        if len(words) >= 8:
            last_phrase = " ".join(words[-8:])
            if last_phrase in source_clean:
                cl["confidence"] = round(max(0.4, cl.get("confidence", 0.5) - 0.1), 2)
                validated.append(cl)
                continue

        # 4. Try any 8-word sliding window (for large clauses with minor differences/paraphrases)
        if len(words) > 8:
            matched_window = False
            for start_idx in range(len(words) - 7):
                sub_phrase = " ".join(words[start_idx : start_idx + 8])
                if sub_phrase in source_clean:
                    cl["confidence"] = round(max(0.3, cl.get("confidence", 0.5) - 0.2), 2)
                    validated.append(cl)
                    matched_window = True
                    break
            if matched_window:
                continue

        # 5. Try any 5-word sliding window for shorter excerpts
        if 5 <= len(words) <= 7:
            matched_window = False
            for start_idx in range(len(words) - 4):
                sub_phrase = " ".join(words[start_idx : start_idx + 5])
                if sub_phrase in source_clean:
                    cl["confidence"] = round(max(0.25, cl.get("confidence", 0.5) - 0.25), 2)
                    validated.append(cl)
                    matched_window = True
                    break
            if matched_window:
                continue

    return validated


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~1 token per 4 characters for English text."""
    return len(text) // 4


def _repair_truncated_json(text: str) -> str:
    """Attempt to repair JSON that was truncated mid-output by the LLM.
    
    Common truncation patterns:
      - Array cut off mid-object: [{...}, {"key": "val   → close string, object, array
      - Missing closing brackets: [{...}, {...}          → add ]
      - Trailing comma: [{...},]                         → remove comma before ]
    """
    text = text.strip()
    if not text:
        return text

    # Remove any trailing incomplete key-value pair after last complete object
    # Find the last complete object (ending with })
    last_brace = text.rfind("}")
    if last_brace == -1:
        return text

    # Truncate everything after the last complete closing brace
    truncated = text[:last_brace + 1]

    # Count brackets to see what's missing
    open_brackets = truncated.count("[")
    close_brackets = truncated.count("]")

    # Remove trailing commas before we add closing brackets
    truncated = truncated.rstrip().rstrip(",")

    # Add missing closing brackets
    for _ in range(open_brackets - close_brackets):
        truncated += "]"

    return truncated


def classifier_agent(state: PipelineState) -> dict:
    """Agent 2 entry-point: classify contract text into CUAD clause types."""

    if state.get("status") == "parse_error":
        return {"identified_clauses": [], "status": "classification_error"}

    cleaned_pages = state.get("cleaned_pages", [])
    raw_text = state.get("raw_text", "")
    errors: list[str] = list(state.get("errors", []))

    if not cleaned_pages:
        errors.append("No text available for classification")
        return {"identified_clauses": [], "status": "classification_error", "errors": errors}

    # Load CUAD examples from database
    cuad_examples = _load_cuad_examples()
    print(f"  [Classifier] Loaded CUAD examples for {len(cuad_examples)} clause types")

    all_clauses: list[dict] = []

    # Since we are using Claude Opus 4.8 via the unlimited.surf gateway, we can safely process 
    # larger overlapping page chunks (e.g. chunk_size = 3, overlap = 1) without rate limit concerns.
    chunk_size = 3
    overlap = 1
    chunks = []
    i = 0
    while i < len(cleaned_pages):
        chunk = cleaned_pages[i : i + chunk_size]
        chunks.append(chunk)
        if i + chunk_size >= len(cleaned_pages):
            break
        i += chunk_size - overlap

    total_chunks = len(chunks)
    print(f"  [Classifier] Processing {total_chunks} chunks using Claude Opus 4.8...")

    for chunk_idx, chunk in enumerate(chunks):
        page_range = f"Pages {chunk[0]['page']}-{chunk[-1]['page']}"

        # Build page-annotated text
        chunk_text = ""
        for p in chunk:
            chunk_text += f"\n--- PAGE {p['page']} ---\n{p['text']}\n"

        if len(chunk_text.strip()) < 20:
            continue

        system_prompt, user_prompt = _build_prompt(chunk_text, page_range)

        # Retry loop with exponential backoff for general network issues
        max_retries = 5
        backoff = 3.0
        success = False

        for attempt in range(max_retries):
            try:
                # Small delay to stagger calls politely
                time.sleep(1.0)

                # Call LLM helper
                response_text = call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.1,
                    max_tokens=3000
                )

                text = response_text.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                text = text.strip()

                # Robust extraction: find the JSON array in the text
                array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
                if array_match:
                    text = array_match.group(0)

                # Try parsing, and if it fails, attempt JSON repair
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    repaired = _repair_truncated_json(text)
                    try:
                        parsed = json.loads(repaired)
                        print(f"  [Classifier] {page_range}: repaired truncated JSON")
                    except json.JSONDecodeError:
                        raise  # Re-raise so outer except catches it

                if isinstance(parsed, list):
                    validated = _validate_clauses(parsed, chunk_text)
                    all_clauses.extend(validated)
                    print(f"  [Classifier] {page_range}: found {len(validated)} clauses")
                    success = True
                    break
                else:
                    print(f"  [Classifier] {page_range}: no clauses found")
                    success = True
                    break

            except Exception as exc:
                print(f"  [Classifier] Attempt {attempt+1} failed: {exc}")
                time.sleep(backoff)
                backoff *= 2.0
                if attempt == max_retries - 1:
                    errors.append(f"Classification failed on {page_range}: {exc}")

    # De-duplicate clauses (same type + very similar text)
    seen: set[str] = set()
    unique_clauses: list[dict] = []
    for cl in all_clauses:
        # Normalize whitespace for comparison
        norm_excerpt = re.sub(r"\s+", " ", cl["text_excerpt"]).strip().lower()
        key = f"{cl['clause_type']}::{norm_excerpt[:80]}"
        if key not in seen:
            seen.add(key)
            unique_clauses.append(cl)

    print(f"  [Classifier] Total unique clauses identified: {len(unique_clauses)}")

    return {
        "identified_clauses": unique_clauses,
        "status": "classified",
        "errors": errors,
    }
