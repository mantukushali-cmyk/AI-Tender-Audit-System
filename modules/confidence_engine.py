import re

# Phrasing that strongly implies a mandatory bidder requirement
MANDATORY_PHRASES = [
    "shall submit", "must submit", "shall furnish", "must furnish",
    "to be submitted", "to be uploaded", "along with the bid",
    "mandatorily required", "hard copy submitted", "enclose"
]

# Phrasing that implies informational, reference, or post-award contexts
REJECT_PHRASES = [
    "for information only", "sample format", "proforma only", 
    "issued after award", "post-award", "successful bidder shall",
    "will be issued by owner", "for reference", "not mandatory"
]

# Boost if the evidence explicitly contains structural document nouns
DOCUMENT_KEYWORDS = [
    "certificate", "declaration", "undertaking", "authorization", 
    "datasheet", "compliance", "power of attorney", "receipt"
]

def calculate_confidence_score(alias_type, evidence, total_occurrences):
    """
    Calculates a deterministic structural confidence score between 0 and 100.
    """
    score = 0
    evidence_lower = evidence.lower().strip()

    # 1. Base Assignment via Alias Matching Quality
    if alias_type == "exact":
        score += 40
    elif alias_type == "regex":
        score += 30
    elif alias_type == "fuzzy":
        score += 15

    # 2. Frequency Check (Recurring documents have higher contextual relevance)
    score += min(total_occurrences * 5, 15)

    # 3. Mandate Phrasing Check
    for phrase in MANDATORY_PHRASES:
        if phrase in evidence_lower:
            score += 10
            break  # Apply once to prevent artificial inflation

    # 4. Explicit Document Language Boost
    if any(word in evidence_lower for word in DOCUMENT_KEYWORDS):
        score += 10

    # 5. Informational/Reference Penalty Deductions
    for phrase in REJECT_PHRASES:
        if phrase in evidence_lower:
            score -= 30
            break 

    # Constrain boundary limits
    return max(0, min(score, 100))


def route_candidate(score):
    """
    Determines pipeline routing based on production confidence thresholds.
    """
    if score >= 75:
        return "AUTO_ACCEPT"
    elif score >= 50:
        return "VERIFY_WITH_LLM"
    else:
        return "REJECT"