import json
import re
import traceback
import ollama


def verify_page_content(
    page_text: str,
    target_doc_key: str,
    doc_description: str = ""
) -> dict:
    """
    Verify whether a single PDF page contains the required document.
    """

    prompt = f"""
You are an expert Indian Government Tender Document Auditor.

Your task is to determine whether THIS SINGLE PAGE belongs to the requested bidder document.

====================================================
REQUIRED DOCUMENT
====================================================

Document Name:
{target_doc_key}

Description:
{doc_description}

====================================================
PAGE CONTENT
====================================================

{page_text}

====================================================
IMPORTANT
====================================================

Analyze ONLY THIS PAGE.

Do NOT use previous pages or future pages.

Ignore OCR mistakes, spelling mistakes, broken words, missing spaces, punctuation errors and formatting issues.

Do NOT require the exact document title.

Instead, identify the document using:

• document structure
• purpose
• content
• identifiers
• issuing authority
• signatures
• seals
• certificate layout

A page is VERIFIED only if it is part of the ACTUAL uploaded document.

A page is NOT VERIFIED if it merely instructs the bidder to submit that document.

====================================================
EXAMPLES
====================================================

Example 1

Tender says:

"The bidder shall submit PAN Card."

Result

status = not_found

Reason:
This is only a tender requirement.

----------------------------------------------------

Example 2

Page contains:

Permanent Account Number
ABCDE1234F
Income Tax Department
Name of Holder

Result

status = verified

----------------------------------------------------

Example 3

Tender says

Manufacturer Authorization Form shall be submitted.

status = not_found

----------------------------------------------------

Example 4

OEM Letter

"We hereby authorize M/s ABC Pvt Ltd to quote and supply..."

Tender No:
Authorized Signatory
Company Seal

status = verified

====================================================
GENERAL VERIFICATION RULES
====================================================

A page is VERIFIED only when it contains the actual uploaded document.

A page is NOT VERIFIED when it is:

• tender instruction
• eligibility criteria
• checklist
• annexure index
• list of required documents
• technical specification
• BOQ
• scope of work
• payment terms
• commercial terms
• contract conditions
• cover page
• table of contents
• declaration that only mentions another document

Never verify using only one keyword.

Use the complete context of the page.

====================================================
DOCUMENT RECOGNITION
====================================================

PAN Card

Strong evidence

• Permanent Account Number
• PAN Number
• Income Tax Department
• Holder Name
• Father's Name
• Date of Birth

----------------------------------------------------

GST Registration Certificate

Strong evidence

• GSTIN
• Goods and Services Tax
• Registration Certificate
• Legal Name
• Trade Name
• Principal Place of Business
• Registration Date

----------------------------------------------------

Certificate of Incorporation

Strong evidence

• Ministry of Corporate Affairs
• Registrar of Companies
• CIN
• Company Name
• Date of Incorporation

----------------------------------------------------

MSME / UDYAM Certificate

Strong evidence

• UDYAM
• MSME
• Udyam Registration Number
• Government of India
• Enterprise Name

----------------------------------------------------

Manufacturer Authorization Form (MAF)

Strong evidence

• Manufacturer Letterhead
• Manufacturer Authorization
• Manufacturer's Authorization Form
• OEM Authorization
• We hereby authorize
• We authorize M/s
• Authorized Dealer
• Authorized Partner
• Tender Number
• Bid Number
• Product Name
• Authorized Signatory
• Company Seal

A tender instruction mentioning MAF is NOT VERIFIED.

----------------------------------------------------

OEM Certificate

Strong evidence

• Original Equipment Manufacturer
• OEM Certificate
• Manufacturing Facility
• Manufacturer Declaration

----------------------------------------------------

Bank Guarantee

Strong evidence

• Bank Guarantee
• BG Number
• Issuing Bank
• Beneficiary
• Guarantee Amount
• Validity
• Bank Seal

----------------------------------------------------

Insurance Surety Bond

Strong evidence

• Insurance Surety Bond
• ISB
• Bond Number
• Insurance Company
• Principal
• Obligee
• Bond Amount
• Authorized Signatory

----------------------------------------------------

Surety Bond

Strong evidence

• Surety Bond
• Performance Surety
• Bid Surety
• Principal
• Obligee
• Bond Number

----------------------------------------------------

Power of Attorney

Strong evidence

• Power of Attorney
• Attorney Holder
• Constitute and Appoint
• Authorized Representative
• Execute
• Sign on behalf

----------------------------------------------------

Integrity Pact

Strong evidence

• Integrity Pact
• Independent External Monitor
• Corrupt Practice
• Bribery

----------------------------------------------------

Blacklisting Declaration

Strong evidence

• Not Blacklisted
• Not Debarred
• Holiday Listing
• Blacklisting Declaration

----------------------------------------------------

Experience Certificate

Strong evidence

• Client Name
• Project
• Work Executed
• Completion
• Performance

----------------------------------------------------

Completion Certificate

Strong evidence

• Completion Certificate
• Successfully Completed
• Completion Date
• Client

----------------------------------------------------

Technical Datasheet

Strong evidence

• Product Model
• Technical Specifications
• Dimensions
• Features
• Manufacturer

----------------------------------------------------

Compliance Sheet

Strong evidence

• Compliance Matrix
• Clause
• Offered
• Complied
• Yes / No

----------------------------------------------------

Brochure

Strong evidence

• Product Images
• Catalogue
• Product Features
• Specifications

----------------------------------------------------

Invoice

Strong evidence

• Tax Invoice
• Invoice Number
• Invoice Date
• GSTIN

----------------------------------------------------

Inspection Release Note

Strong evidence

• Inspection
• Release Note
• Dispatch Clearance

----------------------------------------------------

Test Certificate

Strong evidence

• Test Certificate
• Material Test Report
• MTC

====================================================
DECISION RULES
====================================================

95-100

Clearly the requested uploaded document.

80-94

Strong evidence.
Minor information missing.

60-79

Some evidence.
Cannot be completely certain.

40-59

Mostly instructions.
Not enough evidence.

0-39

Definitely another document.

====================================================
UNREADABLE DOCUMENT RULES
====================================================

Return status = "unreadable" if:

• The page appears to be an uploaded document.
• OCR text is mostly unreadable.
• Characters are corrupted.
• Important fields cannot be identified.
• The scan is blurred.
• Large portions of the page are missing.
• The page is heavily skewed or cropped.

Examples:

A scanned PAN Card where only random characters are readable.

A blurred GST Certificate.

A Manufacturer Authorization Letter that cannot be read because OCR failed.

Do NOT return "not_found" for unreadable documents.

Return "unreadable" whenever the page appears to contain a document but there is insufficient readable evidence to verify it.

====================================================
FINAL CHECK
====================================================

Before answering ask yourself:

"Is this page the actual uploaded document?"

OR

"Is this page merely asking the bidder to submit the document?"

If it is only asking for submission,

status MUST be not_found.

====================================================
RETURN ONLY JSON
====================================================

Return ONLY valid JSON in exactly this format:

{{
    "status": "not_found",
    "confidence_percentage": 0,
    "evidence_snippet": "short text",
    "reasoning": "why"
}}

Where status must be ONE of:

- "verified"
- "unreadable"
- "not_found"
"""

    try:
        response = ollama.chat(
            model="gemma3:4b",
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Indian Government Tender Document Auditor.\n"
                        "Return ONLY valid JSON.\n"
                        "Do not explain.\n"
                        "Do not use markdown."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "top_p": 0.9,
                "top_k": 20,
                "repeat_penalty": 1.1,
                "num_predict": 512,
                "num_ctx": 8192,
                "num_thread": 8
            }
        )
        

        print("\n========== RAW RESPONSE ==========")
        print(response.model_dump())
        print("==================================")

        content = response.get("message", {}).get("content", "").strip()

        if not content:
            raise Exception("Empty response from Ollama")

        # Remove markdown wrappers if the model ignores constraints
        content = (
            content.replace("```json", "")
                   .replace("```", "")
                   .strip()
        )

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise Exception("No JSON found in Ollama response.")

        json_text = match.group()
        data = json.loads(json_text)

        # Fallback tracking using the new status key strings
        return {
            "status": data.get("status", "not_found"),
            "confidence_percentage": int(data.get("confidence_percentage", 0)),
            "evidence_snippet": data.get("evidence_snippet", ""),
            "reasoning": data.get("reasoning", "")
        }

    except Exception:
        print("\n========== AI CHECK ERROR ==========")
        traceback.print_exc()
        print("====================================")

        return {
            "status": "not_found",
            "confidence_percentage": 0,
            "evidence_snippet": "",
            "reasoning": "Parsing Failed"
        }


def check_document(requirement, page_text):
    return verify_page_content(
        page_text=page_text,
        target_doc_key=requirement,
        doc_description=requirement
    )


# --- Example Execution and UI Display Pipeline ---
if __name__ == "__main__":
    # Mocking sample evaluation scenarios
    requirements = [
        "PAN Card", 
        "GST Registration Certificate", 
        "MAF", 
        "Power of Attorney"
    ]
    
    mock_pages = [
        "Permanent Account Number ABCDE1234F Income Tax Department Name: Partha",
        "G5T1N corrupt_data_unreadable_scan ####### Goods and Service Tax",
        "The bidder shall submit a Manufacturer Authorization Form (MAF)",
        "p0w3r 0f aTt0rn3y corrupted OCR layout text block unreadable copy"
    ]

    unreadable_documents = []
    ui_display_rows = []

    for req, text in zip(requirements, mock_pages):
        result = check_document(req, text)
        
        # 2. Logic processing pipeline replacement
        status = result.get("status", "not_found")

        if status == "verified":
            final_status = "Verified"
            ui_icon = "✓ Verified"
        elif status == "unreadable":
            final_status = "Unreadable"
            ui_icon = "⚠ Unreadable"
            # 3. Store the unreadable document name
            unreadable_documents.append(req)
        else:
            final_status = "Missing"
            ui_icon = "✗ Missing"
            
        ui_display_rows.append((req, ui_icon))

    # 4. Print unreadable documents list console report
    print("\nUnreadable Documents")
    for doc in unreadable_documents:
        print("-", doc)

    # 5. Show in your UI Representation
    print("\n\n### UI Output Simulation")
    print(f"| {'Document':<32} | {'Status':<15} |")
    print(f"|{'-'*34}|{'-'*17}|")
    for doc_name, icon in ui_display_rows:
        print(f"| {doc_name:<32} | {icon:<15} |")