"""Parses the CUAD SQuAD-format JSON and seeds the database with clause types and examples."""

import json
import re
from pathlib import Path
from database.connection import SessionLocal, init_db
from database.models import ClauseType, ClauseExample

# All 41 CUAD clause types with descriptions and risk categories
CLAUSE_TYPE_DEFINITIONS = [
    ("Document Name", "The name or title of the contract/agreement.", "LOW"),
    ("Parties", "The names of the contracting parties.", "LOW"),
    ("Agreement Date", "The date when the agreement was signed.", "LOW"),
    ("Effective Date", "The date when the agreement becomes effective.", "LOW"),
    ("Expiration Date", "The date when the agreement expires or terminates.", "MEDIUM"),
    ("Renewal Term", "Terms and conditions for renewal of the agreement.", "MEDIUM"),
    ("Notice Period To Terminate Renewal", "Notice period required to terminate automatic renewal.", "MEDIUM"),
    ("Governing Law", "The jurisdiction whose laws govern the agreement.", "MEDIUM"),
    ("Most Favored Nation", "Clause ensuring equal or better terms than those given to other parties.", "MEDIUM"),
    ("Non-Compete", "Restrictions on competing with the other party during or after the contract.", "HIGH"),
    ("Exclusivity", "Exclusive rights or obligations granted to one party.", "HIGH"),
    ("No-Solicit Of Customers", "Restrictions on soliciting the other party's customers.", "HIGH"),
    ("Competitive Restriction Exception", "Exceptions to competitive restrictions or non-compete clauses.", "MEDIUM"),
    ("No-Solicit Of Employees", "Restrictions on soliciting or hiring the other party's employees.", "HIGH"),
    ("Non-Disparagement", "Obligations not to make negative statements about the other party.", "MEDIUM"),
    ("Termination For Convenience", "Right to terminate the agreement without cause.", "HIGH"),
    ("Rofr/Rofo/Rofn", "Right of First Refusal, First Offer, or First Negotiation.", "MEDIUM"),
    ("Change Of Control", "Provisions triggered by changes in ownership or control of a party.", "HIGH"),
    ("Anti-Assignment", "Restrictions on assigning rights or obligations to third parties.", "MEDIUM"),
    ("Revenue/Profit Sharing", "Terms for sharing revenue or profits between parties.", "MEDIUM"),
    ("Price Restrictions", "Limitations or controls on pricing of goods or services.", "MEDIUM"),
    ("Minimum Commitment", "Minimum purchase, volume, or performance obligations.", "HIGH"),
    ("Volume Restriction", "Limitations on the volume of goods or services.", "MEDIUM"),
    ("Ip Ownership Assignment", "Transfer of intellectual property ownership rights.", "HIGH"),
    ("Joint Ip Ownership", "Shared ownership of intellectual property created under the agreement.", "HIGH"),
    ("License Grant", "Grant of license to use intellectual property or technology.", "MEDIUM"),
    ("Non-Transferable License", "License that cannot be transferred to third parties.", "LOW"),
    ("Affiliate License-Licensor", "License rights extended to the licensor's affiliates.", "MEDIUM"),
    ("Affiliate License-Licensee", "License rights extended to the licensee's affiliates.", "MEDIUM"),
    ("Unlimited/All-You-Can-Eat-License", "License without usage or volume limitations.", "MEDIUM"),
    ("Irrevocable Or Perpetual License", "License that cannot be revoked or has no end date.", "HIGH"),
    ("Source Code Escrow", "Arrangement to hold source code with a third-party escrow agent.", "MEDIUM"),
    ("Post-Termination Services", "Services or obligations that continue after the agreement terminates.", "MEDIUM"),
    ("Audit Rights", "Rights to audit the other party's records, compliance, or performance.", "MEDIUM"),
    ("Uncapped Liability", "No upper limit on the amount of liability a party may incur.", "HIGH"),
    ("Cap On Liability", "A maximum limit on the total liability of a party.", "MEDIUM"),
    ("Liquidated Damages", "Pre-determined amount of damages payable in case of breach.", "HIGH"),
    ("Warranty Duration", "The period during which warranties remain valid.", "MEDIUM"),
    ("Insurance", "Requirements for maintaining insurance coverage.", "MEDIUM"),
    ("Covenant Not To Sue", "Agreement not to bring legal action against the other party.", "HIGH"),
    ("Third Party Beneficiary", "Rights granted to parties who are not signatories to the contract.", "MEDIUM"),
]

# Mapping from CUAD question patterns to clause type names
QUESTION_TO_CLAUSE = {}
for name, _, _ in CLAUSE_TYPE_DEFINITIONS:
    # The CUAD questions use the format: 'Highlight the parts ... related to "ClauseType"'
    QUESTION_TO_CLAUSE[name.lower()] = name


def extract_clause_type_from_question(question: str) -> str | None:
    """Extract the clause type name from a CUAD question string."""
    # Pattern: Highlight the parts (if any) of this contract related to "Clause Type"
    match = re.search(r'related to ["\u201c]([^"\u201d]+)["\u201d]', question, re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        # Try exact match first
        for name, _, _ in CLAUSE_TYPE_DEFINITIONS:
            if extracted.lower() == name.lower():
                return name
        # Try fuzzy match
        for name, _, _ in CLAUSE_TYPE_DEFINITIONS:
            if extracted.lower().replace(" ", "") == name.lower().replace(" ", ""):
                return name
            if extracted.lower() in name.lower() or name.lower() in extracted.lower():
                return name
    return None


def seed_clause_types(db):
    """Insert the 41 clause type definitions into the database."""
    existing = db.query(ClauseType).count()
    if existing >= 41:
        print(f"  [OK] Clause types already seeded ({existing} types)")
        return

    for name, description, risk_category in CLAUSE_TYPE_DEFINITIONS:
        ct = db.query(ClauseType).filter(ClauseType.name == name).first()
        if not ct:
            ct = ClauseType(name=name, description=description, risk_category=risk_category)
            db.add(ct)

    db.commit()
    count = db.query(ClauseType).count()
    print(f"  [OK] Seeded {count} clause types")


def seed_cuad_examples(db, cuad_json_path: Path, max_examples_per_type: int = 50):
    """Parse the CUAD JSON file and insert example text spans into the database."""
    existing = db.query(ClauseExample).count()
    if existing > 0:
        print(f"  [OK] CUAD examples already seeded ({existing} examples)")
        return

    print(f"  Loading CUAD JSON from {cuad_json_path}...")
    with open(cuad_json_path, "r", encoding="utf-8") as f:
        cuad_data = json.load(f)

    # Build a name -> ClauseType mapping
    clause_type_map = {}
    for ct in db.query(ClauseType).all():
        clause_type_map[ct.name.lower()] = ct

    examples_count = {name.lower(): 0 for name, _, _ in CLAUSE_TYPE_DEFINITIONS}
    total_added = 0

    for contract in cuad_data.get("data", []):
        contract_title = contract.get("title", "unknown")

        for paragraph in contract.get("paragraphs", []):
            for qa in paragraph.get("qas", []):
                question = qa.get("question", "")
                answers = qa.get("answers", [])
                is_impossible = qa.get("is_impossible", True)

                if is_impossible or not answers:
                    continue

                clause_name = extract_clause_type_from_question(question)
                if not clause_name:
                    continue

                key = clause_name.lower()
                if key not in clause_type_map:
                    continue

                if examples_count[key] >= max_examples_per_type:
                    continue

                ct = clause_type_map[key]

                for answer in answers:
                    text_span = answer.get("text", "").strip()
                    if not text_span or len(text_span) < 5:
                        continue

                    # Avoid duplicates
                    if examples_count[key] >= max_examples_per_type:
                        break

                    example = ClauseExample(
                        clause_type_id=ct.id,
                        source_contract=contract_title,
                        text_span=text_span
                    )
                    db.add(example)
                    examples_count[key] += 1
                    total_added += 1

        # Commit in batches per contract
        if total_added % 500 == 0 and total_added > 0:
            db.commit()

    db.commit()
    print(f"  [OK] Seeded {total_added} CUAD examples across clause types")

    # Print distribution
    for name, _, _ in CLAUSE_TYPE_DEFINITIONS:
        count = examples_count.get(name.lower(), 0)
        if count > 0:
            print(f"    {name}: {count} examples")
