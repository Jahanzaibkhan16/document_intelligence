# 📄 Document Intelligence System

AI-powered document extraction — supports invoices, receipts, ID cards, resumes, bank statements, purchase orders, business cards, and utility bills.

## Features

- **8 document types** with auto-detection
- **Batch upload** — process 50+ files at once
- **Excel export** — grouped by document type
- **PDF reports** — combined summaries
- **Search** — find documents by any field
- **Statistics** — dashboard with charts

## Supported Formats

- PDF (text + scanned)
- Images: JPG, PNG, TIFF, BMP
- Word: DOCX
- Text: TXT, MD

## Tech Stack

- Python 3.11
- Streamlit (web UI)
- Google Gemini AI (extraction)
- Tesseract OCR (scanned docs)
- SQLite (storage)
- openpyxl + fpdf2 (exports)

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/document_intelligence.git
cd document_intelligence
pip install -r requirements.txt
# Add your GEMINI_API_KEY to .env
streamlit run src/ui/app.py