import json
import traceback
from modules.ollama_client import ask_gemma

def clean_and_repair_json(raw_str: str) -> str:
    """
    Cleans structural garbage, handles unescaped characters, and strips trailing 
    commas commonly dropped by local LLMs inside large arrays.
    """
    if not raw_str:
        return ""
    
    raw_str = raw_str.strip()
    import re
    match = re.search(r"\{.*\}", raw_str, re.DOTALL)
    if match:
        raw_str = match.group()

    pattern = r"(\"evidence\"\s*:\s*\"[^\"]*?)(\n|\t)([^\"]*?\")"
    while re.search(pattern, raw_str):
        raw_str = re.sub(pattern, r"\1 \3", raw_str)

    raw_str = re.sub(r",\s*\]", "]", raw_str)
    raw_str = re.sub(r",\s*\}", "}", raw_str)

    return raw_str

def verify_medium_confidence_batch(medium_confidence_batch: dict) -> dict:
    """
    Sends a batch of borderline candidates to Gemma for a strict binary 
    (TRUE/FALSE) compliance determination based on the isolated evidence.
    """
    if not medium_confidence_batch:
        return {}

    print(f"Batching Pass 2 Verification for {len(medium_confidence_batch)} documents...")
    
    batch_items = list(medium_confidence_batch.values())
    items_text = ""

    for item in batch_items:
        items_text += f"\nDocument: {item['document_name']}\nEvidence: {item['evidence'][:300]}\n"

    pass2_batch_prompt = f"""For every document answer only TRUE or FALSE.

TRUE: The bidder must submit this document with the bid.
FALSE: It is only a format, sample, reference, specification, or post-award document.

Return JSON only. Include every document listed below.

{{
  "verification_results": {{
    "<document_name>": true,
    "<document_name>": false
  }}
}}

DOCUMENTS:
{items_text}
"""
    try:
        raw_verification = ask_gemma(pass2_batch_prompt)
        repaired_json_str = clean_and_repair_json(raw_verification)
        v_payload = json.loads(repaired_json_str)
        return v_payload.get("verification_results", {})
        
    except Exception:
        print(f"Pass 2 verification exception structural handling: {traceback.format_exc()}")
        # Fallback: Default to accepting if the LLM crashes or returns corrupt text
        return {key: True for key in medium_confidence_batch}