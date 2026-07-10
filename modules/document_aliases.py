# modules/document_aliases.py
import re
import unicodedata
from rapidfuzz import process, fuzz
from modules.alias_learner import find_learned_match, learn_alias

# -------------------------------------------------------------------------
# 1. FLAT CACHE INITIALIZATION (Solves the O(n²) Loop Problem)
# -------------------------------------------------------------------------
DOCUMENT_ALIASES = {
    "PAN Card": ["PAN", "PAN Card", "Permanent Account Number", "Copy of PAN", "Income Tax PAN", "PAN Certificate", "PAN Details"],
    "Certificate of Incorporation": ["Certificate of Incorporation", "COI", "Company Incorporation", "Company Registration Certificate", "Registrar of Companies Certificate", "ROC Certificate"],
    "MSME Certificate": ["MSME", "MSME Registration", "Udyam Registration", "Udyam Certificate", "SSI Certificate", "Small Scale Industry Certificate"],
    "GST Registration Certificate": ["GST", "GSTIN", "GST Registration", "GST Registration Certificate", "Goods and Services Tax", "FORM GST REG-06", "REGISTRATION CERTIFICATE", "GST Number"],
    "Trade License": ["Trade License", "Trade Licence", "Trade Certificate", "Municipal Trade License"],
    "Factory License": ["Factory License", "Factory Licence"],
    "Bank Guarantee": ["Bank Guarantee", "Performance Bank Guarantee", "PBG"],
    "Bid Security": ["Bid Security", "Tender Security", "EMD", "Earnest Money Deposit", "Bid Bond", "Bid Security Declaration", "EMD Declaration", "Tender Fee Security"],
    "Bid Security Declaration": ["Bid Security Declaration", "BSD", "Bid Security Declaration Format"],
    "Solvency Certificate": ["Solvency Certificate", "Bank Solvency", "Financial Solvency", "Net Worth Certificate", "Bank Solvency Certificate"],
    "Audited Balance Sheet": ["Balance Sheet", "Audited Balance Sheet", "Annual Balance Sheet", "Financial Statement"],
    "Profit and Loss Statement": ["Profit & Loss", "P&L Statement", "Income Statement", "Profit and Loss Account"],
    "Turnover Certificate": ["Turnover Certificate", "Annual Turnover", "Average Annual Turnover"],
    "Insurance Surety Bond (ISB)": ["insurance surety bond", "insurance surety", "insurance guarantee", "insurance bond", "isb"],
    "Surety Bond": ["surety bond", "bid surety", "performance surety", "contract surety"],
    "Manufacturer Authorization Form": ["MAF", "Manufacturer Authorization", "Manufacturer Authorization Form", "Manufacturer Authorization Letter", "OEM Authorization", "OEM Authorization Letter", "OEM Certificate", "Authorization from Manufacturer"],
    "OEM Certificate": ["OEM Certificate", "Original Equipment Manufacturer", "Manufacturer Certificate", "OEM Declaration"],
    "BIS Certificate": ["BIS", "BIS Certificate", "Bureau of Indian Standards Certificate"],
    "Technical Datasheet": ["Technical Datasheet", "Data Sheet", "Datasheet", "Product Datasheet"],
    "Compliance Sheet": ["compliance sheet", "compliance matrix", "technical compliance sheet"],
    "Brochure": ["Brochure", "Catalogue", "Catalog", "Product Catalogue", "Technical Brochure"],
    "Technical Deviation Statement": ["Deviation Statement", "Technical Deviation", "Technical Deviation Statement"],
    "Property Title Deed": ["Title Deed", "Sale Deed", "Ownership Document", "Property Deeds", "Possession Certificate", "Land Layout"],
    "Encumbrance Certificate": ["Encumbrance Certificate", "EC", "Encumbrance Proof"],
    "Property Tax Receipt": ["Property Tax", "Tax Receipt", "Mutation Copy", "Khata Certificate", "Khata"],
    "Driving License": ["Driving License", "DL", "Driver License"],
    "Registration Certificate (RC)": ["RC Book", "Registration Certificate", "Vehicle Registration", "Vehicle RC"],
    "Completion Certificate": ["Completion Certificate", "Project Completion Certificate", "Work Completion Certificate", "Execution Certificate", "Completion Report"],
    "Experience Certificate": ["Experience Certificate", "Past Experience", "Work Experience", "Performance Certificate", "Client Certificate", "Experience Details", "Executed Projects"],
    "Work Order": ["Work Order", "Purchase Order", "Supply Order", "PO", "WO", "Letter of Award", "LOA", "Letter of Intent", "LOI", "Contract Agreement"],
    "ISO 9001 Certificate": ["ISO 9001", "ISO Certificate", "Quality Management Certificate", "QMS Certificate"],
    "ISO 14001 Certificate": ["ISO 14001", "Environmental Management System", "EMS Certificate"],
    "ISO 45001 Certificate": ["ISO 45001", "OHSMS", "Occupational Health and Safety Certificate"],
    "Insurance Policy": ["Insurance Policy", "Insurance Certificate", "General Insurance", "Liability Insurance"],
    "Fire Safety Certificate": ["Fire NOC", "Fire Safety Certificate", "Fire Clearance", "Fire Approval"],
    "Warranty Certificate": ["Warranty", "Warranty Certificate", "Warranty Declaration", "Warranty Letter"],
    "Power of Attorney": ["Power of Attorney", "POA", "Authorization Letter", "Authority Letter", "Letter of Authorization"],
    "Undertaking": ["Undertaking", "General Undertaking", "Bid Undertaking", "Undertaking Letter"],
    "Integrity Pact": ["Integrity Pact", "Integrity Agreement", "Integrity Declaration"],
    "Non-Blacklisting Declaration": ["Non Blacklisting", "Blacklist Declaration", "Holiday Listing Declaration", "No Blacklisting Certificate"],
    "Blacklisting Declaration": ["Blacklisting Declaration", "Declaration of Blacklisting", "Declaration of Black Listing", "Not Blacklisted", "No Blacklisting"],
    "Insolvency & Bankruptcy Declaration": ["Insolvency", "Insolvency Declaration", "Bankruptcy Declaration", "IBC", "Insolvency and Bankruptcy Code","Declaration of Insolvency & Bankruptcy",
    "Declaration of Insolvency and Bankruptcy",
    "Declaration under Insolvency and Bankruptcy Code",
    "Declaration regarding Insolvency and Bankruptcy",
    "Declaration of Proceedings under Insolvency and Bankruptcy Code",
    "Declaration of Proceedings under IBC",
    "Declaration under IBC"],
    "GFR Border Certificate": ["Certificate On Restrictions Under Rule 144(Xi) Of GFRs (Country Border)", "Rule 144(Xi)", "Country Border Certificate"],
    "GFR TOT Certificate": ["Certificate On Restrictions Under Rule 144(Xi) Of GFRs (TOT Arrangement)", "TOT Arrangement Certificate", "Transfer of Technology Certificate"],
    "PPP MII Undertaking": ["PPP MII", "Undertaking of PPP MII", "Make in India Undertaking", "Local Content Declaration"],
    "Registration Certificates": ["Registration Certificate", "Registration Certificates", "Company Registration", "Firm Registration", "Business Registration"],
    "ATC (Annexure-B)": ["atc", "annexure-b", "annexure b", "atc (annexure-b)", "acceptance of tender conditions"],
    "Annexures": ["Annexure", "Annexures", "Annexure-A", "Annexure-B", "Annexure-C", "Annexure-I", "Annexure-II"],
    "Technical Datasheet": [
        "Technical Compliance",
        "Technical Datasheet",
        "Technical Data Sheet",
        "Technical Specification",
        "Technical Specifications",
        "Compliance Sheet",
        "Compliance Matrix",
        "Technical Offer",
        "Specification Sheet"
   ]
}

# Compile Flat Structure Once on Module Load: O(1) matching setup
ALL_ALIASES = []
ALIAS_TO_STANDARD = {}

for standard_key, aliases in DOCUMENT_ALIASES.items():
    # Standard key acts as its own alias lookup
    std_lower = standard_key.strip().lower()
    ALL_ALIASES.append(std_lower)
    ALIAS_TO_STANDARD[std_lower] = standard_key
    
    for alias in aliases:
        alias_lower = alias.strip().lower()
        if alias_lower not in ALIAS_TO_STANDARD:
            ALL_ALIASES.append(alias_lower)
            ALIAS_TO_STANDARD[alias_lower] = standard_key


# -------------------------------------------------------------------------
# 2. SANITIZATION PIPELINE (Unicode + Normalized Punctuation)
# -------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """
    Cleans up OCR artifacts, applies Unicode normalization, preserves structure,
    and replaces smart quotes/dashes smoothly.
    """
    if not text:
        return ""
    
    # Unicode Normalization (Form KC decomposes curly quotes and weird accents)
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    
    # Map directional/uncommon punctuation to standardized text formatting
    punctuation_map = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "—": "-", "–": "-", "―": "-",  # Em/En dashes
        "\n": " ", "\t": " "            # Structural formatting spacing
    }
    for bad, good in punctuation_map.items():
        text = text.replace(bad, good)
        
    # Standardize spaces but retain structural hyphenation like GST-REG-06 or ISO-9001
    text = re.sub(r"[\[\](){}<>|\\/_~`+*=$%^#@•°]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_document_rules(cleaned_name: str) -> bool:
    """
    Hard Reject Gate & Quality Validation Framework.
    Filters out structural boilerplate text before hitting fuzzy layers.
    """
    INVALID_PHRASES = [
        "signature", "seal", "stamp", "authorized signatory", "invoice", "vendor invoice",
        "technical recommendation", "recommendation", "technical specification", "technical specifications",
        "scope of work", "evaluation criteria", "payment terms", "delivery schedule", "vendor classification",
        "loss control", "packing material", "mail id", "mobile no", "telephone", "electricity bill",
        "address proof details", "policy", "rule", "clause", "bank details", "company's letter head",
        "company letter head", "letter head", "sender to receiver", "receiver information", "format enclosed",
        "tender documents"
    ]
    if any(p in cleaned_name for p in INVALID_PHRASES):
        return False

    VALID_HINTS = [
        "certificate", "card", "registration", "license", "licence", "form", "undertaking",
        "declaration", "affidavit", "authorization", "authorisation", "letter", "agreement",
        "guarantee", "bond", "cheque", "work order", "purchase order", "annexure", "datasheet",
        "brochure", "compliance sheet", "pact", "pan", "gst", "coi", "pbg", "emd", "atc"
    ]
    if not any(h in cleaned_name for h in VALID_HINTS):
        return False

    GENERIC_BLOCKLIST = {"declaration", "undertaking", "certificate", "form", "annexure", "documents", "document"}
    if cleaned_name in GENERIC_BLOCKLIST:
        return False

    return True


# -------------------------------------------------------------------------
# 3. CORE RESOLUTION ENGINE
# -------------------------------------------------------------------------
def normalize_document_name(extracted_name: str):
    if not extracted_name:
        return None

    # Step 1: Clean & Normalize Input
    cleaned = normalize_text(extracted_name)
    if not cleaned:
        return None

    # Step 2: Immediate Reject Validation Gate
    if not validate_document_rules(cleaned):
        return None

    # Step 3: Exact Match
    if cleaned in ALIAS_TO_STANDARD:
        return ALIAS_TO_STANDARD[cleaned]

    # Step 4: Regex Word Match (Prevents PAN matching PANEL)
    for alias_lower, standard_key in ALIAS_TO_STANDARD.items():
        if len(alias_lower) > 3:
            # Use raw string word boundary lookup safely matching alphanumeric items
            if re.search(rf"\b{re.escape(alias_lower)}\b", cleaned):
                return standard_key

    # Step 5: Historical Learned Alias Match
    learned = find_learned_match(extracted_name)
    if learned:
        return learned

    # Step 6: Flat-Cache RapidFuzz Search (Strict 93% Threshold Limit)
    # token_set_ratio is resilient to word re-ordering while keeping strict match metrics
    fuzzy_result = process.extractOne(cleaned, ALL_ALIASES, scorer=fuzz.token_set_ratio)
    if fuzzy_result:
        matched_alias, score, _ = fuzzy_result
        if score >= 93.0:
            return ALIAS_TO_STANDARD[matched_alias]

    # Step 7: Safe Learning Review Pipeline Gate
    # High certainty match but non-dictionary entity -> Pushed to Review Queue 
    # instead of damaging the operational file system.
    final_title = extracted_name.strip()
    
    # Check if text contains high-confidence validation indicators before registering learning 
    if len(cleaned) >= 5 and any(word in cleaned for word in ["certificate", "undertaking", "declaration"]):
       
        # Pass data context flags directly to review handler pipeline
        learn_alias(
                raw_alias=final_title, 
                assigned_standard=final_title,
                requires_manual_review=True
            )

    return final_title