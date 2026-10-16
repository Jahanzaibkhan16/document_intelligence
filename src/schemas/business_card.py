# src/schemas/business_card.py
"""Business card schema."""

BUSINESS_CARD_SCHEMA = {
    "type": "business_card",
    "description": "A business or visiting card",
    "fields": {
        "full_name": "Person's name",
        "job_title": "Job title or position",
        "company_name": "Company or business name",
        "department": "Department (if mentioned)",
        "email": "Email address",
        "phone": "Primary phone",
        "mobile": "Mobile number",
        "fax": "Fax number",
        "website": "Company website",
        "address": "Office address",
        "city": "City",
        "country": "Country",
        "postal_code": "Postal/ZIP code",
        "linkedin": "LinkedIn profile",
        "twitter": "Twitter/X handle",
        "other_social": "Other social media",
        "notes": "Additional notes or tagline",
    },
    "required": ["full_name"],
}