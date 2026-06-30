import json
import re
import time
from agents.state import PipelineState
from database.connection import SessionLocal
from database.models import ClauseType, ClauseExample
from config import call_llm

# Predefined metadata list of 41 CUAD types
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

# Fetch training examples per clause type
def _load_cuad_examples() -> dict[str, list[str]]:
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

# Generate classification prompt from contract chunk and page range
def _build_prompt(contract_chunk: str, page_range: str) -> tuple[str, str]:
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

# Verify if identified quotes exist in the source document
def _validate_clauses(clauses: list[dict], source_text: str) -> list[dict]:
    source_clean = re.sub(r"\s+", " ", source_text).lower()
    validated: list[dict] = []

    for cl in clauses:
        excerpt = cl.get("text_excerpt", "").strip()
        if not excerpt or len(excerpt) < 3:
            continue

        if cl.get("clause_type") not in CUAD_TYPES:
            continue

        excerpt_clean = re.sub(r"\s+", " ", excerpt).lower()
        words = excerpt_clean.split()
        if not words:
            continue

        # Look for first 8 words in source
        check_len = min(8, len(words))
        check_phrase = " ".join(words[:check_len])
        if check_phrase in source_clean:
            validated.append(cl)
            continue

        # Look for first 4 words in source
        short_phrase = " ".join(words[:min(4, len(words))])
        if short_phrase in source_clean:
            cl["confidence"] = round(max(0.3, cl.get("confidence", 0.5) - 0.2), 2)
            validated.append(cl)
            continue

        # Look for last 8 words in source
        if len(words) >= 8:
            last_phrase = " ".join(words[-8:])
            if last_phrase in source_clean:
                cl["confidence"] = round(max(0.4, cl.get("confidence", 0.5) - 0.1), 2)
                validated.append(cl)
                continue

        # Check sliding 8-word chunks
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

        # Check sliding 5-word chunks
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

# Calculate rough token count
def _estimate_tokens(text: str) -> int:
    return len(text) // 4

# Repair JSON string cut off during generation
def _repair_truncated_json(text: str) -> str:
    text = text.strip()
    if not text:
        return text

    last_brace = text.rfind("}")
    if last_brace == -1:
        return text

    truncated = text[:last_brace + 1]
    open_brackets = truncated.count("[")
    close_brackets = truncated.count("]")
    truncated = truncated.rstrip().rstrip(",")

    # Append missing close brackets
    for _ in range(open_brackets - close_brackets):
        truncated += "]"

    return truncated

# Process and classify text paragraphs
def classifier_agent(state: PipelineState) -> dict:
    if state.get("status") == "parse_error":
        return {"identified_clauses": [], "status": "classification_error"}

    cleaned_pages = state.get("cleaned_pages", [])
    errors: list[str] = list(state.get("errors", []))

    if not cleaned_pages:
        errors.append("No text available for classification")
        return {"identified_clauses": [], "status": "classification_error", "errors": errors}

    cuad_examples = _load_cuad_examples()
    print(f"  [Classifier] Loaded CUAD examples for {len(cuad_examples)} clause types")

    all_clauses: list[dict] = []

    # Configure pagination chunks for pipeline execution
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

        # Combine page chunks into single body
        chunk_text = ""
        for p in chunk:
            chunk_text += f"\n--- PAGE {p['page']} ---\n{p['text']}\n"

        if len(chunk_text.strip()) < 20:
            continue

        system_prompt, user_prompt = _build_prompt(chunk_text, page_range)

        max_retries = 5
        backoff = 3.0
        success = False

        # Attempt API calls with retries
        for attempt in range(max_retries):
            try:
                time.sleep(3.0)

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

                array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
                if array_match:
                    text = array_match.group(0)

                # Sanitize control characters that Groq sometimes injects
                text = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', text)

                # Parse and repair JSON content
                try:
                    parsed = json.loads(text, strict=False)
                except json.JSONDecodeError:
                    repaired = _repair_truncated_json(text)
                    try:
                        parsed = json.loads(repaired, strict=False)
                        print(f"  [Classifier] {page_range}: repaired truncated JSON")
                    except json.JSONDecodeError:
                        raise

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

    # Remove duplicate matching clauses
    seen: set[str] = set()
    unique_clauses: list[dict] = []
    for cl in all_clauses:
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
