# src/schemas/resume.py
"""Resume / CV schema."""

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