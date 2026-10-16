# src/schemas/registry.py
"""Central registry — auto-loads all document schemas."""
from src.schemas.invoice import INVOICE_SCHEMA
from src.schemas.receipt import RECEIPT_SCHEMA
from src.schemas.id_card import ID_CARD_SCHEMA
from src.schemas.resume import RESUME_SCHEMA
from src.schemas.bank_statement import BANK_STATEMENT_SCHEMA
from src.schemas.purchase_order import PURCHASE_ORDER_SCHEMA
from src.schemas.business_card import BUSINESS_CARD_SCHEMA
from src.schemas.utility_bill import UTILITY_BILL_SCHEMA


# ================= MASTER REGISTRY =================
# To add a new document type:
#   1. Create a new file in src/schemas/ (e.g., my_type.py)
#   2. Import it here
#   3. Add it to SCHEMAS dict below
SCHEMAS = {
    "invoice": INVOICE_SCHEMA,
    "receipt": RECEIPT_SCHEMA,
    "id_card": ID_CARD_SCHEMA,
    "resume": RESUME_SCHEMA,
    "bank_statement": BANK_STATEMENT_SCHEMA,
    "purchase_order": PURCHASE_ORDER_SCHEMA,
    "business_card": BUSINESS_CARD_SCHEMA,
    "utility_bill": UTILITY_BILL_SCHEMA,
}


# ================= HELPER FUNCTIONS =================
def get_schema(doc_type):
    """Get schema by document type."""
    return SCHEMAS.get(doc_type)


def get_fields_list(doc_type):
    """Get list of field names for a document type."""
    schema = get_schema(doc_type)
    if not schema:
        return []
    return list(schema['fields'].keys())


def get_all_types():
    """Get list of all supported document types."""
    return list(SCHEMAS.keys())


def get_all_descriptions():
    """Get dict of type → description."""
    return {k: v['description'] for k, v in SCHEMAS.items()}


# ================= SELF TEST =================
if __name__ == "__main__":
    print("=" * 60)
    print("REGISTRY TEST")
    print("=" * 60)
    print(f"\n✅ Total document types: {len(SCHEMAS)}\n")

    for name, schema in SCHEMAS.items():
        fields = schema['fields']
        required = schema['required']
        print(f"📄 {name.upper()}")
        print(f"   Fields:   {len(fields)}")
        print(f"   Required: {required}")
        print(f"   {schema['description'][:60]}...")
        print()