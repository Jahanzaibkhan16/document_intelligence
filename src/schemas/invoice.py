# src/schemas/invoice.py
"""Invoice schema."""

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