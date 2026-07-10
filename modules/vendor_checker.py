DOCUMENT_ALIASES = {
    "GST Certificate": [
        "GST",
        "GSTIN",
        "GST Certificate"
    ],

    "PAN Card": [
        "PAN",
        "Permanent Account Number",
        "PAN Card"
    ],

    "Manufacturer Authorization Form": [
        "MAF",
        "Manufacturer Authorization Form",
        "Manufacturer Authorization Letter",
        "OEM Authorization"
    ],

    "Warranty Certificate": [
        "Warranty",
        "Warranty Certificate"
    ]
}

def check_vendor(vendor_text, required_documents):

    results = {}

    vendor_text = vendor_text.lower()

    for doc in required_documents:

        aliases = DOCUMENT_ALIASES.get(doc, [doc])

        found = False

        for alias in aliases:
            if alias.lower() in vendor_text:
                found = True
                break

        results[doc] = "Present" if found else "Missing"

    return results