# src/schemas/bank_statement.py
"""Bank statement schema."""

BANK_STATEMENT_SCHEMA = {
    "type": "bank_statement",
    "description": "A bank account statement showing transactions",
    "fields": {
        "bank_name": "Name of the bank",
        "bank_branch": "Branch name",
        "account_holder": "Account holder name",
        "account_number": "Account number (mask if possible)",
        "account_type": "Savings/Current/Checking",
        "statement_period_start": "Start date of statement (YYYY-MM-DD)",
        "statement_period_end": "End date of statement (YYYY-MM-DD)",
        "opening_balance": "Opening balance amount",
        "closing_balance": "Closing balance amount",
        "total_credits": "Total money in",
        "total_debits": "Total money out",
        "transactions": "List: [{date, description, debit, credit, balance}]",
        "currency": "Currency code",
        "iban": "IBAN if present",
        "swift_code": "SWIFT/BIC code if present",
        "notes": "Additional notes",
    },
    "required": ["bank_name", "account_number"],
}