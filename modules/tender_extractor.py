# modules/tender_extractor.py

import json
import re
import traceback
from modules.document_aliases import normalize_document_name
from modules.ollama_client import ask_gemma  # Directly integrated centralized client module
from modules.rule_extractor import extract_candidates
from modules.verifier import verify_medium_confidence_batch
# -------------------------------------------------------------------------
# 1. ARCHITECTURAL CONSTANTS & SCORING MATRICES
# -------------------------------------------------------------------------
# Step 1 & 4 Implementation: Weighted keyword scoring net for high-precision page routing
PAGE_SCORING_WEIGHTS = {
    "documents to be submitted": 20,
    "checklist of documents": 20,
    "documents required": 18,
    "bidder shall submit": 15,
    "documents to accompany": 15,
    "to be uploaded": 15,
    "technical bid documents": 15,
    "commercial bid documents": 15,
    "pre qualification": 12,
    "eligibility criteria": 10,
    "annexure": 8,

}

PAGE_SCORE_THRESHOLD = 8 # Minimum aggregate score required to scan a page region

# Step 2 Implementation: Highly targeted phrase nets for rule-based verification
MANDATORY_REGEX_PATTERNS = [
    r"\bshall\s+submit\b", r"\bmust\s+submit\b", r"\bbidder\s+shall\s+furnish\b",
    r"\bupload\b", r"\benclose\b", r"\battach\b", r"\bmandatory\b", r"\brequired\b",
    r"\bto\s+be\s+furnished\b", r"\bto\s+be\s+uploaded\b"
]

REJECT_REGEX_PATTERNS = [
    r"\bfor\s+information\s+only\b", r"\bsample\b", r"\bformat\s+only\b",
    r"\bpost\s*-?\s*award\b", r"\bafter\s+award\b", r"\boptional\b",
    r"\bif\s+applicable\b", r"\bnot\s+mandatory\b", r"\bnot\s+required\b",
    r"\bissued by purchaser\b",
    r"\bissued after award\b",
    r"\bwill be issued\b",
    r"\bfor reference only\b",
    r"\bspecification\b",
    r"\bgeneral information\b",
    r"\bprice schedule\b"
]

# Step 8 Implementation: Granular Multi-Domain UI Categories
EXPANDED_CATEGORIES = {
    "Identity", "Financial", "Technical", "Experience", "OEM", "Legal",
    "Government Policy", "Safety", "Environmental", "Property", "Transport", "Other"
}
def clean_and_repair_json(raw_str: str) -> str:
    """
    Cleans structural garbage, handles unescaped characters, and strips trailing 
    commas commonly dropped by local LLMs inside large arrays.
    """
    if not raw_str:
        return ""
    
    # Extract only the content within the outermost curly braces if the LLM added prose
    raw_str = raw_str.strip()
    match = re.search(r"\{.*\}", raw_str, re.DOTALL)
    if match:
        raw_str = match.group()

    # FIX: Recursively remove ALL raw newlines or tabs trapped inside string values
    # until no unescaped format control characters remain in the text quotes
    pattern = r"(\"evidence\"\s*:\s*\"[^\"]*?)(\n|\t)([^\"]*?\")"
    while re.search(pattern, raw_str):
        raw_str = re.sub(pattern, r"\1 \3", raw_str)

    # Fix trailing commas inside arrays/objects right before closing brackets
    raw_str = re.sub(r",\s*\]", "]", raw_str)
    raw_str = re.sub(r",\s*\}", "}", raw_str)

    return raw_str
# -------------------------------------------------------------------------
# 2. CORE RULE ENGINE UTILITIES
# -------------------------------------------------------------------------
def score_and_select_pages(processed_pages: list) -> list:
    """
    Dynamically scores pages and clumps them into small, manageable 
    contextual windows to prevent LLM token overflow.
    """
    scored_indices = []
    
    for idx, page in enumerate(processed_pages):
        text_lower = page["text"].lower()
        score = 0
        for phrase, weight in PAGE_SCORING_WEIGHTS.items():
            if phrase in text_lower:
                score += min(weight * text_lower.count(phrase), weight * 3)
        if score >= PAGE_SCORE_THRESHOLD:
            scored_indices.append(idx)
            
    if not scored_indices:
        return []

    # FIX: Window Creation with a maximum page-length limit
    MAX_CHARS = 6000

    windows = []
    current_window = []
    current_chars = 0

    for idx in sorted(set(scored_indices)):

        page_chars = len(processed_pages[idx]["text"])

        if current_chars + page_chars > MAX_CHARS:
            windows.append(current_window)
            current_window = [idx]
            current_chars = page_chars
        else:
            current_window.append(idx)
            current_chars += page_chars

    if current_window:
        windows.append(current_window)

    return windows

DOCUMENT_SECTION_HEADERS = [
    "documents to be submitted",
    "checklist of documents",
    "documents required",
    "documents to accompany",
    "documents to upload",
    "technical bid documents",
    "commercial bid documents",
    "pre qualification",
    "eligibility criteria",
]

def extract_document_sections(text):
    text_lower = text.lower()

    for header in DOCUMENT_SECTION_HEADERS:
        pos = text_lower.find(header)
        if pos != -1:
            return text[pos:]

    return text

def calculate_confidence_score(has_llm, alias_type, evidence, total_occurrences):
    
    score = 0
    evidence_lower = evidence.lower().strip()

    # ----------------------------------------------------
    # 1. Alias Quality (Most Important)
    # ----------------------------------------------------
    if alias_type == "exact":
        score += 40
    elif alias_type == "regex":
        score += 35
    elif alias_type == "fuzzy":
        score += 20

    # ----------------------------------------------------
    # 2. Multiple Occurrences
    # ----------------------------------------------------
    score += min(total_occurrences * 5, 15)

    # ----------------------------------------------------
    # 3. Strong Mandatory Evidence
    # ----------------------------------------------------
    mandatory_phrases = [
        "shall submit",
        "must submit",
        "shall furnish",
        "to be submitted",
        "to be uploaded",
        "along with the bid",
        "upload",
        "enclose",
        "attach",
        "mandatory",
        "required",
    ]

    for phrase in mandatory_phrases:
        if phrase in evidence_lower:
            score += 8

    # ----------------------------------------------------
    # 4. Reject Informational Evidence
    # ----------------------------------------------------
    reject_phrases = [
        "for information only",
        "sample",
        "format only",
        "issued after award",
        "post-award",
        "optional",
        "if applicable",
        "not mandatory",
        "not required",
        "general information",
        "technical specification",
        "price schedule",
        "will be issued",
        "issued by purchaser",
        "issued by owner",
    ]

    for phrase in reject_phrases:
        if phrase in evidence_lower:
            score -= 25

    # ----------------------------------------------------
    # 5. Bonus for Document Keywords
    # ----------------------------------------------------
    document_words = [
        "certificate",
        "declaration",
        "undertaking",
        "authorization",
        "datasheet",
        "compliance",
        "power of attorney",
        "bank guarantee",
        "work order",
        "completion certificate",
    ]

    if any(word in evidence_lower for word in document_words):
        score += 10

    # ----------------------------------------------------
    # 6. LLM Verification Bonus
    # ----------------------------------------------------
    if has_llm:
        score += 10

    return max(0, min(score, 100))

# -------------------------------------------------------------------------
# 3. HIGH-PRECISION EXTRACTION PIPELINE
# -------------------------------------------------------------------------
def extract_requirements(pages: list) -> dict:
    all_candidates = {}  # Tracks structural items across deduplication checks
    processed_pages = []
    verified_documents = set()
    
    # Structural Ingestion Map
    for idx, page in enumerate(pages):
        p_num = page.get('page', idx + 1) if isinstance(page, dict) else idx + 1
        p_text = page.get('text', '') if isinstance(page, dict) else str(page)
        processed_pages.append({"page": p_num, "text": p_text})

    # Step 1: Smarter Dynamic Page/Window Selection
    windows = score_and_select_pages(processed_pages)
    print("=" * 60)
    print("Selected windows:", windows)
    print("=" * 60)
    if not windows:
        return {"required_documents": []}

    # Pass 1 Loop Execution Framework
    for window in windows:
        chunk_pages = []

        for i in window:
            page_text = extract_document_sections(processed_pages[i]["text"])

            chunk_pages.append(
                f"--- PAGE {processed_pages[i]['page']} ---\n{page_text}"
            )

        chunk_text = "\n\n".join(chunk_pages)
        print(f"Processing window: {window}")
        print(f"Chunk size: {len(chunk_text):,} characters")
        
        # Step 6 Implementation: Explicit Negative Constraints to block model hallucinations
        pass1_prompt = f"""You are an expert in Indian Government Procurement (IOCL, GeM, CPWD, NTPC, BHEL, ONGC, HPCL).

Your task is to identify EVERY document that the bidder is required to submit with the bid.

Extract documents appearing under headings such as:

- Documents to be Submitted
- Checklist
- Annexure
- Proforma
- Declaration
- Undertaking
- Authorization
- Certificate
- Format
- Affidavit
- Statement

If the text contains phrases like

- shall submit
- shall furnish
- to be submitted
- upload
- enclose
- along with the bid
- techno-commercial bid

then extract the document.

Treat a document as mandatory ONLY if it is listed under:
- Documents to be submitted
- Check List of Documents
- Documents to accompany the bid
- Technical Bid Documents
- Commercial Bid Documents
- Mandatory Documents
- Annexure / Proforma required with the bid

A Technical Datasheet, Compliance Sheet, Brochure, or Catalog is mandatory ONLY when it appears in one of these sections or is explicitly required by phrases such as:
- shall submit
- must submit
- to be submitted
- upload
- attach
- enclose
- required with the bid

Do NOT extract Technical Datasheet or Compliance Sheet if they are mentioned only as part of technical specifications or product descriptions.

Examples:

PROFORMA FOR DECLARATION ON PROCEEDINGS UNDER INSOLVENCY AND BANKRUPTCY
→ Insolvency & Bankruptcy Declaration

GENERAL UNDERTAKING
→ Undertaking

PROFORMA FOR BANK MANDATE FORMAT
→ Bank Mandate

PROFORMA FOR DEVIATIONS-TECHNICAL
→ Technical Deviation Statement

DECLARATION OF BLACKLISTING
→ Blacklisting Declaration

MANUFACTURER AUTHORIZATION LETTER
→ Manufacturer Authorization Form

{{
  "candidates": [
    {{
      "document_name": "example name",
      "category": "one of the allowed strings",
      "page_number": 1,
      "evidence": "matching sentence text from context"
    }}
  ]
}}

=== CONTEXT TEXT ===
{chunk_text}
"""
        try:
            print("=" * 80)
            print("WINDOW INDEXES :", window)
            print("WINDOW PAGES   :", [processed_pages[i]["page"] for i in window])
            print("Prompt length  :", len(pass1_prompt))
            print("Chunk length   :", len(chunk_text))
            print("=" * 80)

            print("----- OCR PREVIEW (First 1500 chars) -----")
            print(chunk_text[:1500])
            print("------------------------------------------")

            
            candidates_list = extract_candidates(chunk_text)
            
            # Step 5 & 9 Implementation: Immediate Extraction Normalization & Data Merging
            for cand in candidates_list:
                # ... (rest of your candidate iteration code remains exactly the same)
                raw_name = cand.get("document_name", "").strip()
                evidence_str = cand.get("evidence", "").strip()
                page_num = cand.get("page_number")
                category = cand.get("category", "Other")
                
                if not raw_name:
                    continue
                    
                INVALID_NAMES = {
                    "information",
                    "certificate",
                    "statement",
                    "format",
                    "proforma",
                    "details",
                    "annexure",
                    "specification",
                    "section",
                    "table",
                    "schedule"
                }

                raw_lower = raw_name.lower().strip()

                if (
                    raw_lower in INVALID_NAMES
                    or raw_lower.startswith("format")
                    or raw_lower.startswith("annexure")
                    or raw_lower.startswith("statement")
                    or raw_lower.startswith("certificate")
                    or raw_lower.startswith("information")
                ):
                    continue
                # Normalize via 7-Layer engine (Includes Regex Word Boundary and Caching guards)
                resolved_key = normalize_document_name(raw_name)
                if resolved_key in verified_documents:
                    continue
                if not resolved_key:
                    continue
                CHECKLIST_HEADERS = [
                    "documents to be submitted",
                    "check list of documents",
                    "checklist of documents",
                    "documents to accompany",
                    "technical bid documents",
                    "commercial bid documents",
                    "mandatory documents",
                ]

                page_text = ""

                for p in processed_pages:
                    if p["page"] == page_num:
                        page_text = p["text"].lower()
                        break

                TECHNICAL_HINTS = [
                    "technical pqc",
                    "technical datasheet",
                    "datasheet",
                    "data sheet",
                    "brochure",
                    "catalog",
                    "technical specification",
                    "compliance sheet",
                ]

                if any(word in raw_name.lower() for word in ["datasheet", "compliance", "brochure", "catalog"]):
                    evidence_lower = evidence_str.lower()

                    if not (
                        any(header in page_text for header in CHECKLIST_HEADERS)
                        or any(hint in page_text for hint in TECHNICAL_HINTS)
                        or any(hint in evidence_lower for hint in TECHNICAL_HINTS)
                    ):
                        continue 
                # Step 9 Implementation: Merge multi-page evidences rather than dropping occurrences
                if resolved_key not in all_candidates:
                    all_candidates[resolved_key] = {
                        "key": resolved_key,
                        "original_names": [raw_name],
                        "category": category,
                        "pages": [page_num] if page_num else [],
                        "evidences": [evidence_str] if evidence_str else [],
                        "occurrences": 1
                    }
                else:
                    all_candidates[resolved_key]["occurrences"] += 1
                    if page_num and page_num not in all_candidates[resolved_key]["pages"]:
                        all_candidates[resolved_key]["pages"].append(page_num)
                    if evidence_str and evidence_str not in all_candidates[resolved_key]["evidences"]:
                        all_candidates[resolved_key]["evidences"].append(evidence_str)
                        
        except Exception:
            print(f"Extraction execution exception encountered: {traceback.format_exc()}")
            continue

   # -------------------------------------------------------------------------
   # HYBRID BATCH VERIFICATION LAYER (Delegated to verifier.py)
   # -------------------------------------------------------------------------
    final_verified_documents = []
    medium_confidence_batch = {}

    print(f"--- Starting Verification Engine for {len(all_candidates)} candidates ---")
    
    for key, data in all_candidates.items():
        primary_evidence = data["evidences"][0] if data["evidences"] else ""
        
        alias_type = "fuzzy"
        if any(data["key"].lower() == name.lower() for name in data["original_names"]):
            alias_type = "exact"
            
        confidence = calculate_confidence_score(
            has_llm=True, 
            alias_type=alias_type, 
            evidence=primary_evidence, 
            total_occurrences=data["occurrences"]
        )
        print(f"{key} -> Confidence={confidence}")
        
        data["confidence_score"] = confidence

        if confidence >= 75:
            # Auto Accept (Skip LLM Pass)
            final_verified_documents.append({
                "key": data["key"],
                "original_names": list(set(data["original_names"])),
                "category": data["category"],
                "pages": sorted(set(data["pages"])),
                "evidences": data["evidences"],
                "confidence_score": confidence,
                "status": "Verified"
            })
            verified_documents.add(data["key"])

        elif confidence >= 50:
            # Queue up for Batch LLM Verification
            medium_confidence_batch[key] = {
                "document_name": key,
                "confidence": confidence,
                "evidence": primary_evidence
            }
        else:
            continue

    # Execute Batch Pass 2 evaluation via modular verifier
    if medium_confidence_batch:
        from modules.verifier import verify_medium_confidence_batch
        
        results_map = verify_medium_confidence_batch(medium_confidence_batch)

        for key in medium_confidence_batch:
            data = all_candidates[key]
            llm_result = results_map.get(key, True)  # Fallback to True if key dropped

            final_verified_documents.append({
                "key": data["key"],
                "original_names": list(set(data["original_names"])),
                "category": data["category"],
                "pages": sorted(set(data["pages"])),
                "evidences": data["evidences"],
                "confidence_score": data["confidence_score"],
                "status": "Verified" if llm_result else "Rejected",
                "llm_verified": llm_result
            })

    print("FINAL VERIFIED:", len(final_verified_documents))
    for d in final_verified_documents:
        print(f"[{d['status']}] -> {d['key']}")

    return {"required_documents": final_verified_documents}