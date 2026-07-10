# document_patterns.py
import re

DOCUMENT_PATTERNS = {
    # =========================
    # IDENTITY & REGISTRATION
    # =========================
    "PAN Card": [
        r"\b[pP][aA][nN]\s*(card|no|number)?\s*[:\-]?\s*[A-Z]{5}[0-9]{4}[A-Z]\b",
        r"permanent\s+account\s+number",
        r"income\s+tax\s+department"
    ],

    "GST Registration Certificate": [
        r"gst\s*(in|no|number)?\s*[:\-]?\s*[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}",
        r"form\s+gst\s*reg[-_\s]*06\b",
        r"goods\s+and\s+services\s+tax",
        r"principal\s+place\s+of\s+business"
    ],

    "Certificate of Incorporation": [
        r"certificate\s+of\s+incorporation",
        r"registrar\s+of\s+companies",
        r"corporate\s+identity\s+number",
        r"\bCIN\b"
    ],

    "MSME Certificate": [
        r"udyam[-\s]*registration[-\s]*certificate",
        r"udyam[-\s]*[0-9]{12,16}",
        r"ministry\s+of\s+micro\s*,?\s*small",
        r"\bmsme\b"
    ],

    "Trade License": [
        r"trade\s+licen[cs]e\s*(no|number)?\s*[:\-]?\s*[a-zA-Z0-9/-]+",
        r"municipal\s+trade\s+licen[cs]e",
        r"trade\s+certificate"
    ],

    "Factory License": [
        r"factory\s+licen[cs]e",
        r"licen[cs]e\s+under\s+the\s+factories\s+act"
    ],

    "BIS Certificate": [
        r"bureau\s+of\s+indian\s+standards",
        r"\bbis\b\s*(registration|certificate)?",
        r"is\s*/\s*iec\s*certified"
    ],

    "IEC Certificate": [
        r"import\s+export\s+code",
        r"\biec\b\s*(certificate|no|number)?",
        r"dgft"
    ],

    "Cancelled Cheque": [
        r"cancelled\s+cheque",
        r"cancelled\s+check",
        r"ifsc\s*code\s*[:\-]?\s*[A-Z]{4}0[A-Z0-9]{6}"
    ],

    "Address Proof": [
        r"electricity\s+bill",
        r"telephone\s+bill",
        r"utility\s+bill"
    ],

    # =========================
    # FINANCIAL
    # =========================
    "Bank Guarantee": [
        r"bank\s+guarantee\s*(no|number)?\s*[:\-]?\s*[a-zA-Z0-9/-]+",
        r"performance\s+security\s+guarantee",
        r"unconditional\s+and\s+irrevocable\s+bank\s+guarantee"
    ],

    "Bid Security": [
        r"earnest\s+money\s+deposit",
        r"\bemd\b",
        r"demand\s+draft\s*(no|number)?\s*[:\-]?\s*[0-9]+"
    ],

    "Solvency Certificate": [
        r"solvency\s+certificate",
        r"financial\s+soundness"
    ],

    "Audited Balance Sheet": [
        r"balance\s+sheet\s+as\s+at",
        r"auditor'?s\s+report"
    ],

    "Profit and Loss Statement": [
        r"profit\s*&\s*loss",
        r"statement\s+of\s+profit\s+and\s+loss"
    ],

    "Turnover Certificate": [
        r"udin\s*[:\-]?\s*[0-9]{18}",
        r"annual\s+turnover"
    ],

    # =========================
    # OEM / AUTHORIZATION
    # =========================
    "Manufacturer Authorization Form": [
        r"manufacturer['’]?\s*authori[sz]ation\s*form",
        r"we\s+hereby\s+authori[sz]e",
        r"\boem\s+authori[sz]ation\b"
    ],

    "OEM Certificate": [
        r"original\s+equipment\s+manufacturer",
        r"\boem\b\s*certificate"
    ],

    # =========================
    # EXPERIENCE
    # =========================
    "Work Order": [
        r"work\s+order\s*(no|number)?\s*[:\-]?\s*[a-zA-Z0-9/-]+",
        r"purchase\s+order\s*(no|number)?",
        r"contract\s+agreement\s*(no|number)?"
    ],

    "Completion Certificate": [
        r"completion\s+certificate",
        r"successfully\s+completed"
    ],

    "Experience Certificate": [
        r"experience\s+certificate",
        r"satisfactorily\s+executed"
    ],

    # =========================
    # TECHNICAL
    # =========================
    "Technical Datasheet": [
        r"technical\s+compliance",
        r"technical\s+specification",
        r"technical\s+specifications",
        r"technical\s+data\s*sheet",
        r"technical\s+datasheet",
        r"compliance\s+sheet",
        r"compliance\s+matrix"
    ],

    "Compliance Sheet": [
        r"compliance\s+(matrix|statement|sheet)",
        r"technical\s+compliance"
    ],

    "Brochure": [
        r"product\s+(catalogue|catalog|brochure)"
    ],

    # =========================
    # QUALITY / ISO
    # =========================
    "ISO 9001 Certificate": [
        r"iso\s*9001\s*[:\-]?\s*(2015|2008)",
        r"quality\s+management\s+system"
    ],

    "ISO 14001 Certificate": [
        r"iso\s*14001",
        r"environmental\s+management\s+system"
    ],

    "ISO 45001 Certificate": [
        r"iso\s*45001",
        r"occupational\s+health\s+and\s+safety"
    ],

    # =========================
    # LEGAL
    # =========================
    "Power of Attorney": [
        r"power\s+of\s+attorney",
        r"know\s+all\s+men\s+by\s+these\s+presents"
    ],

    "Undertaking": [
        r"undertaking",
        r"solemnly\s+affirm"
    ],

    "Integrity Pact": [
        r"integrity\s+pact"
    ],

    "Blacklisting Declaration": [
        r"not\s+blacklisted",
        r"non[-\s]*blacklisting",
        r"not\s+debarred"
    ],

    # =========================
    # SAFETY / INSURANCE
    # =========================
    "Insurance Policy": [
        r"insurance\s+policy",
        r"policy\s*(number|no)?\s*[:\-]?\s*[a-zA-Z0-9/-]+"
    ],

    "Fire Safety Certificate": [
        r"fire\s+safety\s+certificate",
        r"fire\s+noc"
    ],

    "Warranty Certificate": [
        r"warranty\s+certificate",
        r"warranty\s+period"
    ],

    # =========================
    # SPECIAL TENDER DOCS
    # =========================
    "Annexures": [
        r"\bannexure\s*[-_\s]*[a-z0-9]+\b",
        r"\bannexure\s+[ivx]+\b"
    ],

    "ATC (Annexure-B)": [
        r"acceptance\s+of\s+tender\s+conditions",
        r"\batc\b.*annexure\s*[-_\s]*b"
    ],

    "Insurance Surety Bond (ISB)": [
        r"insurance\s+surety\s+bond",
        r"\bisb\b"
    ],

    "Surety Bond": [
        r"surety\s+bond",
        r"performance\s+surety"
    ],

    "Bid Security Declaration": [
        r"bid\s+security\s+declaration",
        r"\bbsd\b"
    ]
}





def scan_text_for_patterns(text: str, doc_type: str) -> bool:
    patterns = DOCUMENT_PATTERNS.get(doc_type, [])
    if not patterns:
        return False

    text = text.lower()

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False