# src/schemas/document_schemas.py
"""
Structured schemas for different document types.
Each schema defines what fields we want to extract.
"""


# ================= INVOICE =================
INVOICE_SCHEMA = {
    "type": "invoice",
    "description": "A commercial invoice or bill for goods/services",
    "fields": {
        "invoice_number": "Unique invoice identifier",
        "invoice_date": "Date invoice was issued (YYYY-MM-DD)",
        "due_date": "Payment due date (YYYY-MM-DD)",
        "vendor_name": "Seller/company name",
        "vendor_address": "Seller's full address",
        "vendor_phone": "Seller's phone",
        "vendor_email": "Seller's email",
        "vendor_tax_id": "Seller's tax/GST/NTN number",
        "customer_name": "Buyer name or company",
        "customer_address": "Buyer's address",
        "customer_phone": "Buyer's phone",
        "customer_email": "Buyer's email",
        "line_items": "List of items: [{description, quantity, unit_price, total}]",
        "subtotal": "Sum before tax",
        "tax_rate": "Tax percentage",
        "tax_amount": "Total tax amount",
        "discount": "Any discount applied",
        "shipping": "Shipping charges",
        "total_amount": "Final total",
        "currency": "Currency code (USD, PKR, etc.)",
        "payment_terms": "Terms of payment",
        "notes": "Any additional notes",
    },
    "required": ["invoice_number", "vendor_name", "total_amount"],
}


# ================= RECEIPT =================
RECEIPT_SCHEMA = {
    "type": "receipt",
    "description": "A payment receipt or cash memo",
    "fields": {
        "receipt_number": "Receipt number",
        "receipt_date": "Date of purchase",
        "receipt_time": "Time of purchase",
        "store_name": "Shop or business name",
        "store_address": "Store address",
        "store_phone": "Store phone",
        "store_tax_id": "Store tax/NTN number",
        "cashier": "Cashier name or ID",
        "items": "List of items: [{name, quantity, price}]",
        "subtotal": "Subtotal before tax",
        "tax": "Tax amount",
        "discount": "Discount applied",
        "total": "Final total paid",
        "payment_method": "Cash/Card/Mobile",
        "currency": "Currency code",
        "notes": "Additional notes",
    },
    "required": ["store_name", "total"],
}


# ================= ID CARD =================
ID_CARD_SCHEMA = {
    "type": "id_card",
    "description": "National ID card, passport, driving license, or employee ID",
    "fields": {
        "id_type": "Type: national_id, passport, driving_license, employee_id",
        "id_number": "ID/Passport/CNIC number",
        "full_name": "Person's full name",
        "father_name": "Father's name (if present)",
        "mother_name": "Mother's name (if present)",
        "date_of_birth": "DOB (YYYY-MM-DD)",
        "gender": "Male/Female/Other",
        "nationality": "Country of nationality",
        "religion": "Religion (if present)",
        "address": "Residential address",
        "issue_date": "Date of issue",
        "expiry_date": "Date of expiry",
        "issuing_authority": "Government/office that issued",
        "photo_present": "Is there a photo on the card? (yes/no)",
    },
    "required": ["id_number"],
}


# ================= RESUME =================
RESUME_SCHEMA = {
    "type": "resume",
    "description": "CV or resume for a job application",
    "fields": {
        "full_name": "Candidate's full name",
        "email": "Email address",
        "phone": "Phone number",
        "address": "Location/address",
        "linkedin": "LinkedIn URL",
        "portfolio": "Portfolio/GitHub URL",
        "summary": "Professional summary/objective",
        "skills": "List of key skills",
        "languages": "Languages known",
        "education": "List: [{degree, institution, year, grade}]",
        "experience": "List: [{title, company, duration, description}]",
        "certifications": "List of certifications",
        "projects": "List of projects",
        "achievements": "Awards and achievements",
        "references": "References (if listed)",
    },
    "required": ["full_name"],
}


# ================= REGISTRY =================
SCHEMAS = {
    "invoice": INVOICE_SCHEMA,
    "receipt": RECEIPT_SCHEMA,
    "id_card": ID_CARD_SCHEMA,
    "resume": RESUME_SCHEMA,
}


def get_schema(doc_type: str) -> dict:
    """Get a schema by document type."""
    return SCHEMAS.get(doc_type)


def get_fields_list(doc_type: str) -> list:
    """Get list of field names for a document type."""
    schema = get_schema(doc_type)
    if not schema:
        return []
    return list(schema['fields'].keys())


# ================= SELF TEST =================
if __name__ == "__main__":
    print("=" * 60)
    print("SCHEMAS TEST")
    print("=" * 60)

    for name, schema in SCHEMAS.items():
        fields = schema['fields']
        required = schema['required']
        print(f"\n📄 {name.upper()}")
        print(f"   Fields: {len(fields)}")
        print(f"   Required: {required}")
        print(f"   Description: {schema['description'][:60]}...")