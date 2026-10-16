# src/schemas/utility_bill.py
"""Utility bill schema — electricity, gas, water, internet."""

UTILITY_BILL_SCHEMA = {
    "type": "utility_bill",
    "description": "An electricity, gas, water, or internet bill",
    "fields": {
        "bill_type": "electricity / gas / water / internet / phone",
        "provider_name": "Utility company name",
        "provider_phone": "Customer service phone",
        "provider_website": "Company website",
        "account_number": "Customer account number",
        "meter_number": "Meter or connection number",
        "consumer_name": "Customer name",
        "service_address": "Address where service is provided",
        "billing_address": "Mailing address if different",
        "bill_date": "Date bill was issued (YYYY-MM-DD)",
        "due_date": "Payment due date",
        "billing_period_start": "Start of billing period",
        "billing_period_end": "End of billing period",
        "previous_reading": "Previous meter reading",
        "current_reading": "Current meter reading",
        "units_consumed": "Units used (kWh, m³, GB, etc.)",
        "unit_type": "Unit type (kWh, m³, GB)",
        "amount_due": "Total amount due",
        "previous_balance": "Any previous balance",
        "tax_amount": "Tax amount",
        "currency": "Currency code",
        "payment_status": "Paid / Unpaid / Overdue",
        "notes": "Any additional notes",
    },
    "required": ["provider_name", "account_number"],
}