# document_matcher.py
import re
from modules.document_aliases import normalize_document_name
from modules.document_keywords import DOCUMENT_KEYWORDS 

def match_page_for_document(
    page_text: str,
    requirement_name: str,
    lower_page_text: str = None
):
    """
    Pure keyword & alias based document matcher.
    """

    if lower_page_text is None:
        lower_page_text = page_text.lower()

    # --------------------------------------------------
    # Normalize requirement
    # --------------------------------------------------
    standard_doc = normalize_document_name(requirement_name)

    if standard_doc and standard_doc in DOCUMENT_KEYWORDS:
        aliases = DOCUMENT_KEYWORDS[standard_doc]
    elif requirement_name in DOCUMENT_KEYWORDS:
        standard_doc = requirement_name
        aliases = DOCUMENT_KEYWORDS[requirement_name]
    else:
        standard_doc = requirement_name
        aliases = [requirement_name]

    # --------------------------------------------------
    # Alias Matching (Optimized for special characters)
    # --------------------------------------------------
    matched_aliases = []

    for alias in aliases:
        alias_clean = alias.strip().lower()
        if not alias_clean:
            continue

        # Alphanumeric uses word boundaries; symbols use broad substring checking.
        if alias_clean.isalnum():
            pattern = r"\b" + re.escape(alias_clean) + r"\b"
            if re.search(pattern, lower_page_text):
                matched_aliases.append(alias)
        else:
            if alias_clean in lower_page_text:
                matched_aliases.append(alias)

    alias_hits = len(matched_aliases)

    # --------------------------------------------------
    # Structural Anchors
    # --------------------------------------------------
    anchors = [
        "certificate", "registration", "declaration", "undertaking", 
        "proforma", "annexure", "authorization", "authorisation", 
        "bid security", "emd", "bank guarantee", "gst", "pan", 
        "oem", "manufacturer","shall submit",
        "shall furnish",
        "to be submitted",
        "upload",
        "enclose",
        "mandatory",
        "required",
        "along with the bid",
        "techno-commercial bid",
        "commercial bid"
    ]

    anchor_hits = []
    for anchor in anchors:
        if anchor in lower_page_text:
            anchor_hits.append(anchor)

    # --------------------------------------------------
    # Confidence Score Assignment
    # --------------------------------------------------
    confidence = 0.10

    if alias_hits >= 2:
        confidence = 0.95

    elif alias_hits == 1:
        confidence = 0.90

    elif len(anchor_hits) >= 2:
        confidence = 0.50

    elif len(anchor_hits) == 1:
        confidence = 0.30

    evidence = page_text[:250].replace("\n", " ")

    return {
        "requirement": requirement_name,
        "standard_name": standard_doc,
        "is_candidate": confidence >= 0.25,
        "confidence_score": confidence,
        "matched_keywords": matched_aliases,
        "matched_anchor_words": anchor_hits,
        "evidence_snippet": evidence
    }