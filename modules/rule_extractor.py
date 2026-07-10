import re
from modules.document_aliases import DOCUMENT_ALIASES

# Comprehensive production list of mandatory indicator phrases
MANDATORY_WORDS = [
    r"shall\s+submit", 
    r"must\s+submit", 
    r"shall\s+furnish", 
    r"must\s+furnish",
    r"to\s+be\s+submitted", 
    r"to\s+be\s+uploaded", 
    r"shall\s+upload",
    r"\bupload\b", 
    r"\benclose\b", 
    r"\battach\b",
    r"along\s+with\s+the\s+bid",
    r"mandatorily\s+required"
]

# Pre-compile the mandatory pattern check for execution speed
MANDATORY_REGEX = re.compile("|".join(MANDATORY_WORDS), re.IGNORECASE)

def split_into_sentences(text):
    """
    Splits text into actual sentences safely without breaking on common 
    abbreviations like 'i.e.', 'e.g.', 'Co.', or decimal points.
    """
    # Tokenizes sentences by looking for updates followed by whitespace and capital letters
    sentence_end = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\n)\s+(?=[A-Z0-9])')
    return [s.strip() for s in sentence_end.split(text) if s.strip()]

def extract_candidates(text):
    """
    Extracts canonical document names matching patterns inside valid target lines,
    ensuring no duplicate extractions per sentence block.
    """
    candidates = []
    sentences = split_into_sentences(text)

    for sentence in sentences:
        # 1. Look for mandatory structural language using regex bounds
        if not MANDATORY_REGEX.search(sentence):
            continue

        # Track what canonical documents we found in *this specific sentence* to prevent cross-duplication
        found_in_sentence = set()

        # 2. Match aliases using word boundaries to avoid sub-string overlaps (e.g., 'pan' matching 'company')
        for canonical_name, aliases in DOCUMENT_ALIASES.items():
            if canonical_name in found_in_sentence:
                continue
                
            for alias in aliases:
                # Escape the alias safely and wrap it in structural regex word boundaries (\b)
                alias_pattern = re.compile(r'\b' + re.escape(alias.lower()) + r'\b')
                
                if alias_pattern.search(sentence.lower()):
                    candidates.append({
                        "document_name": canonical_name,
                        "evidence": re.sub(r'\s+', ' ', sentence).strip() # Clean layout tabs/newlines
                    })
                    found_in_sentence.add(canonical_name)
                    break  # Found a match for this document group; jump to the next group

    return candidates