# src/test_detection.py
"""Test document type detection for all 8 types."""
from src.processing.ai_extractor import detect_document_type


samples = {
    "invoice": "INVOICE #123\nBill To: XYZ\nTotal: 5000",
    "receipt": "RECEIPT\nThank you for your purchase\nTotal: 250",
    "id_card": "National Identity Card\nCNIC: 12345-6789012-3\nDOB: 1990-01-01",
    "resume": "Resume\nEducation: BS Computer Science\nExperience: 3 years",
    "bank_statement": "Bank Statement\nAccount Number: 0011223344\nOpening Balance: 50000\nClosing Balance: 75000",
    "purchase_order": "PURCHASE ORDER\nPO Number: PO-2025-001\nSupplier: ABC Traders\nDelivery Date: 2025-06-01",
    "business_card": "Business Card\nJohn Smith\nManaging Director\nABC Company",
    "utility_bill": "Electricity Bill\nMeter Reading: 12500\nUnits Consumed: 250 kWh\nDue Date: 2025-06-15",
}

print("=" * 70)
print("DOCUMENT TYPE DETECTION TEST")
print("=" * 70)
print()

correct = 0
for expected, text in samples.items():
    detected = detect_document_type(text)
    ok = "✅" if detected == expected else "❌"
    if detected == expected:
        correct += 1
    print(f"{ok} {expected:20} → detected: {detected}")

print()
print(f"Result: {correct}/{len(samples)} correct")