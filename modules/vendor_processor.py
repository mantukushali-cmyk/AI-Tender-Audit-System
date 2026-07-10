import os

from modules.pdf_reader import extract_pdf_pages
from modules.ai_document_checker import check_document
from modules.document_matcher import match_page_for_document


def process_vendor(vendor_folder, required_documents):
    """
    Fast vendor processing.

    Strategy
    --------
    1. Read each PDF only once.
    2. Build page index.
    3. Use regex matcher first.
    4. Only call LLM for uncertain pages.
    """

    results = {}

    pdf_files = [
        f for f in os.listdir(vendor_folder)
        if f.lower().endswith(".pdf")
    ]

    page_map = []

    # Read every PDF once
    for pdf_file in pdf_files:

        pdf_path = os.path.join(vendor_folder, pdf_file)

        pages = extract_pdf_pages(pdf_path)

        for page in pages:

            text = page["text"] or ""

            page_map.append({
                "file": pdf_file,
                "page": page["page"],
                "text": text,
                "lower": text.lower()
            })

    # -----------------------------
    # Evaluate every requirement
    # -----------------------------
    for requirement in required_documents:

        results[requirement] = {
            "status": "Missing",
            "file": "",
            "page": "",
            "evidence": ""
        }

        regex_candidates = []
        ai_candidates = []

        # Pass 1 : Regex / keyword matching
        for item in page_map:

            try:

                candidate = match_page_for_document(
                    item["text"],
                    requirement,
                    item["lower"]
                )

                score = candidate["confidence_score"]

                if score >= 0.90:
                    regex_candidates.append(
                        (
                          score,
                          item, 
                          candidate
                        )
                    )

                elif score >= 0.50:
                    ai_candidates.append(
                        (
                            score,
                            item
                        )
                    )

                # ignore everything below 0.50

            except Exception:
                continue

        
        # High confidence match found
        if regex_candidates:

            regex_candidates.sort(
                key=lambda x: x[0],
                reverse=True
            )

            _, page, candidate = regex_candidates[0]

            # FIX 1: Extract evidence using keys from document_matcher.py
            evidence_text = candidate.get("evidence_snippet", "")
            if not evidence_text:
                evidence_text = ", ".join(candidate.get("matched_keywords", []))

            # FIX 2: Bind using 'requirement' key to maintain loop mapping dictionary integrity
            results[requirement] = {
                "status": "Present",
                "file": page["file"],
                "page": page["page"],
                "evidence": evidence_text.strip()
            }

            continue
        # ----------------------------------------
        # Pass 2 : AI verification on best candidate pages
        # ----------------------------------------

        # Sort by confidence (highest first)
        ai_candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        # Limit AI verification to top 3 pages
        ai_candidates = ai_candidates[:3]

        for score, item in ai_candidates:

            try:

                response = check_document(
                    requirement,
                    item["text"]
                )

                if response.get("verified", False):

                    results[requirement] = {
                        "status": "Present",
                        "file": item["file"],
                        "page": item["page"],
                        "evidence": response.get(
                            "evidence_snippet",
                            ""
                        )
                    }

                    # Stop after first verified page
                    break

            except Exception:
                continue

    return results