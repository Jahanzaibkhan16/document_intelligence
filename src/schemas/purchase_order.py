# src/schemas/purchase_order.py
"""Purchase Order schema."""

PURCHASE_ORDER_SCHEMA = {
    "type": "purchase_order",
    "description": "A purchase order sent to a supplier",
    "fields": {
        "po_number": "Purchase order number",
        "po_date": "Date PO was created (YYYY-MM-DD)",
        "expected_delivery_date": "Expected delivery date",
        "buyer_name": "Buyer's company name",
        "buyer_address": "Buyer's address",
        "buyer_phone": "Buyer's phone",
        "buyer_email": "Buyer's email",
        "buyer_tax_id": "Buyer's tax ID",
        "supplier_name": "Supplier/vendor name",
        "supplier_address": "Supplier's address",
        "supplier_phone": "Supplier's phone",
        "supplier_email": "Supplier's email",
        "shipping_address": "Delivery address",
        "line_items": "List: [{item_code, description, quantity, unit_price, total}]",
        "subtotal": "Subtotal before tax",
        "tax_amount": "Tax amount",
        "shipping_cost": "Shipping charges",
        "total_amount": "Final total",
        "currency": "Currency code",
        "payment_terms": "Payment terms",
        "delivery_terms": "Delivery terms (FOB, CIF, etc.)",
        "special_instructions": "Special notes",
    },
    "required": ["po_number", "supplier_name"],
}