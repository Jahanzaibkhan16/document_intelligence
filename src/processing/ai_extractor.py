# src/processing/ai_extractor.py
"""
AI-powered document extraction using Google Gemini REST API.
Takes raw text → returns structured JSON matching schema.
No SDK needed — uses requests directly.
"""
import json
import time
from typing import Optional

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL
from src.schemas.registry import SCHEMAS, get_schema, get_all_types


# ================= CLIENT (REST API) =================
def _get_client():
    """No-op — we use REST API directly with requests."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in .env")
    return "rest"


# ================= AI CALL =================
def _call_gemini(prompt: str, max_retries: int = 4,
                  timeout: int = 60) -> tuple[bool, str]:
    """Call Gemini REST API directly (no SDK needed)."""
    import requests

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    # Note: if you get "model not found", try switching to:
    # url = (
    #     f"https://generativelanguage.googleapis.com/v1/"
    #     f"models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    # )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096,
        }
    }

    last_err = ""

    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=timeout)

            if r.status_code == 200:
                data = r.json()
                try:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    if text:
                        return True, text.strip()
                    last_err = "Empty response"
                except (KeyError, IndexError) as e:
                    last_err = f"Bad response format: {e}"


            elif r.status_code in (429, 503):

                # 429 = rate limit

                # 503 = server overloaded (temp)

                wait = 20 + (attempt * 15)  # 20s, then 35s

                last_err = f"Server busy ({r.status_code})"

                if attempt < max_retries - 1:
                    print(f"   ⏳ Server busy — waiting {wait}s...")

                    time.sleep(wait)

                    continue


            elif r.status_code in (401, 403):

                return False, f"API key error ({r.status_code})"


            elif r.status_code == 404:

                return False, (

                    f"Model '{GEMINI_MODEL}' not found. "

                    f"Try 'gemini-2.0-flash' or 'gemini-1.5-flash-latest' "

                    f"in config.py"

                )


            else:

                last_err = f"HTTP {r.status_code}: {r.text[:200]}"

        except Exception as e:
            last_err = str(e)
            print(f"⚠️ Attempt {attempt + 1}: {last_err[:100]}")

        if attempt < max_retries - 1:
            time.sleep(3)

    return False, f"AI failed: {last_err}"


# ================= AUTO DETECT =================
def detect_document_type(text: str) -> str:
    """Detect what type of document this is."""
    if not text or len(text) < 20:
        return "unknown"

    text_lower = text.lower()

    # ============ INVOICE ============
    if any(kw in text_lower for kw in [
        "invoice", "bill to", "invoice no", "invoice number",
        "tax invoice", "amount due", "invoice date"
    ]):
        return "invoice"

    # ============ RECEIPT ============
    if any(kw in text_lower for kw in [
        "receipt", "cash memo", "payment received",
        "thank you for your purchase"
    ]):
        return "receipt"

    # ============ ID CARD ============
    if any(kw in text_lower for kw in [
        "cnic", "national identity", "passport", "date of birth",
        "father name", "license number", "id card", "identity card"
    ]):
        return "id_card"

    # ============ RESUME ============
    if any(kw in text_lower for kw in [
        "resume", "curriculum vitae", "objective",
        "education", "experience", "skills"
    ]):
        return "resume"

    # ============ BANK STATEMENT ============
    if any(kw in text_lower for kw in [
        "bank statement", "account statement", "opening balance",
        "closing balance", "account number", "iban", "swift",
        "statement period", "transaction history"
    ]):
        return "bank_statement"

    # ============ PURCHASE ORDER ============
    if any(kw in text_lower for kw in [
        "purchase order", "po number", "po date",
        "supplier", "delivery date", "shipping address"
    ]):
        return "purchase_order"

    # ============ BUSINESS CARD ============
    if any(kw in text_lower for kw in [
        "business card", "visiting card",
        "managing director", "ceo", "founder"
    ]):
        return "business_card"

    # ============ UTILITY BILL ============
    if any(kw in text_lower for kw in [
        "electricity bill", "gas bill", "water bill",
        "utility bill", "meter reading", "units consumed",
        "kwh", "billing period"
    ]):
        return "utility_bill"

    return "unknown"

# ================= EXTRACT =================
def extract_structured(text: str, doc_type: str) -> tuple[bool, dict | str]:
    """
    Extract structured data from text using AI.
    Returns (success, data_dict_or_error_message).
    """
    schema = get_schema(doc_type)
    if not schema:
        return False, f"Unknown document type: {doc_type}"

    # Build field list for prompt
    fields_desc = "\n".join(
        f'  - "{k}": {v}'
        for k, v in schema['fields'].items()
    )

    prompt = f"""You are a document data extraction expert.

Extract structured data from this {doc_type.upper()} document.

DOCUMENT TEXT:
\"\"\"
{text[:8000]}
\"\"\"

REQUIRED FIELDS (extract all you can find):
{fields_desc}

RULES:
1. Return ONLY valid JSON — no other text, no markdown, no code blocks
2. Use null for fields not found in the document
3. For dates, use YYYY-MM-DD format when possible
4. For amounts, use numeric values (no currency symbols)
5. For lists (like line_items), use array of objects
6. Be precise — do not make up data
7. Extract in the language of the document; add English translation if helpful

Return JSON only, starting with {{ and ending with }}:
"""

    ok, response = _call_gemini(prompt)
    if not ok:
        return False, response

    # Parse JSON from response
    data = _parse_json_response(response)
    if data is None:
        return False, f"AI returned invalid JSON:\n{response[:500]}"

    return True, data


def _parse_json_response(text: str) -> Optional[dict]:
    """Extract JSON from AI response (handles markdown wrapping)."""
    if not text:
        return None

    text = text.strip()

    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_str = text[start:end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error: {e}")
        # Try to fix common issues (single quotes)
        json_str = json_str.replace("'", '"')
        try:
            return json.loads(json_str)
        except Exception:
            return None


# ================= MAIN PIPELINE =================
def process_document(text: str,
                      doc_type: Optional[str] = None
                      ) -> tuple[bool, dict | str]:
    """
    Full pipeline: detect type → extract → return data.

    Args:
        text: Raw document text
        doc_type: Optional override for document type

    Returns:
        (success, data_or_error)
        data = {
            'doc_type': str,
            'fields': dict,
            'confidence': float,
        }
    """
    if not text or len(text) < 10:
        return False, "Document text is empty or too short"

    # Auto-detect if not specified
    if not doc_type:
        doc_type = detect_document_type(text)

    if doc_type == "unknown":
        return False, "Could not detect document type"

    # Extract
    ok, result = extract_structured(text, doc_type)
    if not ok:
        return False, result

    # Calculate confidence
    schema = get_schema(doc_type)
    total_fields = len(schema['fields'])
    required_fields = schema['required']

    filled = sum(1 for v in result.values() if v is not None)
    filled_required = sum(1 for f in required_fields
                           if result.get(f) is not None)

    confidence = (filled_required / max(1, len(required_fields))) * 0.6 + \
                 (filled / max(1, total_fields)) * 0.4

    return True, {
        'doc_type': doc_type,
        'fields': result,
        'confidence': round(confidence, 3),
    }


# ================= TEST =================
if __name__ == "__main__":
    print("=" * 60)
    print("AI EXTRACTOR TEST (REST API)")
    print("=" * 60)
    print(f"API Key set: {bool(GEMINI_API_KEY)}")
    print(f"Model:       {GEMINI_MODEL}")
    print()

    # Test with a fake invoice
    sample_text = """
    INVOICE

    Invoice #: INV-2024-001
    Date: 15-01-2024
    Due Date: 30-01-2024

    From:
    Ahmed Traders
    Shop 45, Main Bazaar
    Lahore, Pakistan
    Phone: +92-300-1234567
    NTN: 1234567-8

    Bill To:
    XYZ Corporation
    123 Business Street
    Karachi, Pakistan

    Items:
    1. Office Chair - 5 units x 5000 = 25,000
    2. Office Table - 2 units x 15,000 = 30,000
    3. File Cabinet - 3 units x 8,000 = 24,000

    Subtotal: 79,000
    Tax (17%): 13,430
    Total: 92,430 PKR

    Payment Terms: Net 15
    """

    print("Detecting document type...")
    detected = detect_document_type(sample_text)
    print(f"✅ Detected: {detected}")
    print()

    if GEMINI_API_KEY:
        print("Extracting with AI...")
        ok, result = process_document(sample_text)
        if ok:
            print("✅ Extraction successful!")
            print(f"   Type:       {result['doc_type']}")
            print(f"   Confidence: {result['confidence']}")
            print()
            print("Extracted fields:")
            for key, value in result['fields'].items():
                if value is not None:
                    display_val = str(value)[:60]
                    print(f"   {key}: {display_val}")
        else:
            print(f"❌ Failed: {result}")
    else:
        print("⚠️ Add GEMINI_API_KEY to .env to test AI extraction")