# src/schemas/id_card.py
"""ID card schema — national ID, passport, driving license."""

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