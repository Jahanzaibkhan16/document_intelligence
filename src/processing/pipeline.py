# src/processing/pipeline.py
"""End-to-end pipeline: file → text → AI extract → database."""
import os
import json
from pathlib import Path

from src.core.config import UPLOADS_DIR, EXTRACTED_DIR
from src.core.database import (
    init_db, add_document, update_document
)
from src.processing.extractors import extract_text
from src.processing.ai_extractor import process_document


def process_file(filepath: str, doc_type: str = None) -> dict:
    """
    Full pipeline from file → structured data.

    Returns:
        {
            'success': bool,
            'document_id': int,
            'doc_type': str,
            'fields': dict,
            'confidence': float,
            'error': str (if failed)
        }
    """
    init_db()

    filepath = str(filepath)
    if not os.path.exists(filepath):
        return {"success": False, "error": "File not found"}

    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    file_type = Path(filepath).suffix.lower()

    # Step 1 — Register in DB
    doc_id = add_document(
        filename=filename,
        filepath=filepath,
        file_size=file_size,
        file_type=file_type,
    )
    print(f"📄 Registered document ID: {doc_id}")

    # Step 2 — Extract text
    print("📖 Extracting text...")
    text, method = extract_text(filepath)
    if not text or len(text) < 10:
        update_document(doc_id, status="failed",
                         error_message="Could not extract text")
        return {
            "success": False,
            "document_id": doc_id,
            "error": "Could not extract text from file",
        }

    print(f"✅ Extracted {len(text)} characters via {method}")

    # Step 3 — AI extraction
    print("🤖 AI extraction...")
    ok, result = process_document(text, doc_type=doc_type)

    if not ok:
        update_document(
            doc_id,
            raw_text=text,
            status="failed",
            error_message=str(result),
        )
        return {
            "success": False,
            "document_id": doc_id,
            "error": str(result),
        }

    # Step 4 — Save to DB
    update_document(
        doc_id,
        doc_type=result['doc_type'],
        raw_text=text,
        extracted_json=json.dumps(result['fields'], ensure_ascii=False),
        confidence=result['confidence'],
        status="done",
    )

    # Save a copy to disk too
    out_path = EXTRACTED_DIR / f"doc_{doc_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to database and {out_path}")

    return {
        "success": True,
        "document_id": doc_id,
        "doc_type": result['doc_type'],
        "fields": result['fields'],
        "confidence": result['confidence'],
    }


# ================= TEST =================
if __name__ == "__main__":
    print("=" * 60)
    print("PIPELINE TEST")
    print("=" * 60)

    # Use the sample text as a fake file
    import tempfile
    sample_text = """
    INVOICE
    Invoice #: INV-2025-042
    Date: 20-03-2025
    From: Karachi Electronics, Saddar, Karachi
    Phone: 0300-1111111
    Bill To: Ali Raza, DHA Phase 5, Karachi
    Items:
    1. LED TV - 1 x 85000 = 85000
    2. Washing Machine - 1 x 45000 = 45000
    3. Microwave - 1 x 25000 = 25000
    Subtotal: 155000
    Tax 17%: 26350
    Total: 181350 PKR
    """

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(sample_text)
        temp_path = f.name

    try:
        result = process_file(temp_path)
        print()
        print("=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False)[:1500])
    finally:
        os.unlink(temp_path)