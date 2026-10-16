# 📄 Document Intelligence System

AI-powered document extraction system that reads invoices, receipts, ID cards, resumes, bank statements, purchase orders, business cards, and utility bills — and extracts structured data using Google Gemini AI.

## ✨ Features

- **8 document types** with auto-detection
- **Batch upload** — process 50+ files at once
- **Excel export** — grouped by document type
- **PDF reports** — combined summaries
- **Search** — find documents by any field
- **Statistics dashboard** — charts and insights

## 📁 Supported Formats

- PDF (text + scanned)
- Images: JPG, PNG, TIFF, BMP
- Word: DOCX
- Text: TXT, MD

## 🛠 Tech Stack

- Python 3.11
- Streamlit (web UI)
- Google Gemini AI (extraction)
- Tesseract OCR (scanned docs)
- SQLite (storage)
- openpyxl + fpdf2 (exports)

## 🚀 Run Locally

```bash
git clone https://github.com/Jahanzaibkhan16/document_intelligence.git
cd document_intelligence

python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Create .env with your API key:
# GEMINI_API_KEY=your_key_here

streamlit run src/ui/app.py