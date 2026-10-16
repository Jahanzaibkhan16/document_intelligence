# src/schemas/receipt.py
"""Receipt schema."""

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