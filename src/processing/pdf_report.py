# src/processing/pdf_report.py
"""PDF report card generator — one report per document."""
import json
import os
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from src.core.config import EXTRACTED_DIR
from src.core.database import get_document


# ================= HELPERS =================
def _clean_text(text):
    """Remove non-latin chars for PDF safety."""
    if text is None:
        return ""
    text = str(text)
    result = ""
    for ch in text:
        try:
            ch.encode("latin-1")
            result += ch
        except UnicodeEncodeError:
            result += "?"
    return result


def _header(pdf, title, subtitle=""):
    """Common PDF header."""
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(31, 78, 120)   # dark blue
    pdf.cell(0, 10, "DOCUMENT INTELLIGENCE", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, _clean_text(title), ln=True, align="C")

    if subtitle:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, _clean_text(subtitle), ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    pdf.set_draw_color(200, 200, 200)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(4)


def _section(pdf, title):
    """Section header."""
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 8, "  " + _clean_text(title), ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def _field(pdf, label, value):
    """Render label : value."""
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(55, 7, _clean_text(label) + ":", border=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, _clean_text(value) or "-", ln=True)


def _safe_multicell(pdf, text, height=6):
    """Write text with safe wrapping."""
    pdf.set_x(pdf.l_margin)
    text = _clean_text(text)
    if not text.strip():
        return

    # Break long words
    words = text.split(" ")
    fixed = []
    for w in words:
        if len(w) > 60:
            while len(w) > 60:
                fixed.append(w[:60])
                w = w[60:]
            if w:
                fixed.append(w)
        else:
            fixed.append(w)

    try:
        pdf.multi_cell(0, height, " ".join(fixed))
    except Exception:
        try:
            pdf.cell(0, height, " ".join(fixed)[:100], ln=True)
        except Exception:
            pdf.ln(height)


# ================= PDF GENERATOR =================
def generate_pdf_report(doc_id, filepath=None):
    """
    Generate a PDF report card for one document.

    Args:
        doc_id: document ID
        filepath: output path (None = auto)

    Returns:
        Path to saved PDF
    """
    doc = get_document(doc_id)
    if not doc:
        raise ValueError(f"Document {doc_id} not found")

    # Parse fields
    fields = {}
    if doc.get('extracted_json'):
        try:
            fields = json.loads(doc['extracted_json'])
        except Exception:
            pass

    # Create PDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    title = f"{doc['doc_type'].replace('_', ' ').title() if doc['doc_type'] else 'Document'} Report"
    _header(pdf, title,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ============ DOCUMENT INFO ============
    _section(pdf, "DOCUMENT INFO")
    _field(pdf, "Document ID", str(doc['id']))
    _field(pdf, "Filename", doc['filename'])
    _field(pdf, "Type", (doc['doc_type'] or 'Unknown').replace('_', ' ').title())
    _field(pdf, "Status", doc['status'])
    _field(pdf, "Confidence", f"{(doc['confidence'] or 0)*100:.1f}%")
    _field(pdf, "Uploaded", str(doc['uploaded_on'])[:19])
    pdf.ln(3)

    # ============ EXTRACTED FIELDS ============
    if fields:
        _section(pdf, "EXTRACTED DATA")

        # Separate simple fields and list fields
        simple = {}
        lists = {}
        for k, v in fields.items():
            if isinstance(v, list) and v:
                lists[k] = v
            elif v is not None and v != "" and not isinstance(v, (list, dict)):
                simple[k] = v

        # Simple fields in 2-column table style
        pdf.set_font("Helvetica", "", 10)
        for k, v in simple.items():
            label = k.replace('_', ' ').title()
            _field(pdf, label, str(v)[:100])

        pdf.ln(3)

        # List fields (line items, education, etc.)
        for key, items in lists.items():
            _section(pdf, key.replace('_', ' ').title().upper())

            if not items:
                continue

            if isinstance(items[0], dict):
                # Table
                keys = list(items[0].keys())
                # Limit columns
                keys = keys[:5]

                col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / len(keys)

                # Header row
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(31, 78, 120)
                pdf.set_text_color(255, 255, 255)
                for k in keys:
                    pdf.cell(col_width, 7,
                             _clean_text(k.replace('_', ' ').title())[:20],
                             border=1, align="C", fill=True)
                pdf.ln()

                # Data rows
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(0, 0, 0)
                for item in items[:20]:  # limit rows
                    for k in keys:
                        val = item.get(k, "")
                        pdf.cell(col_width, 6,
                                 _clean_text(str(val))[:25],
                                 border=1)
                    pdf.ln()

                if len(items) > 20:
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.cell(0, 6,
                             f"... and {len(items) - 20} more items",
                             ln=True)

            else:
                # Simple list
                pdf.set_font("Helvetica", "", 10)
                for i, item in enumerate(items[:20], 1):
                    _safe_multicell(pdf, f"  {i}. {item}", 6)

            pdf.ln(3)

    # ============ FOOTER =================
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5,
             f"Document Intelligence System | Doc ID: {doc['id']}",
             ln=True, align="C")

    # Save
    if filepath is None:
        filepath = EXTRACTED_DIR / f"report_doc_{doc_id}.pdf"

    pdf.output(str(filepath))
    return str(filepath)


# ================= TEST =================
if __name__ == "__main__":
    print("=" * 60)
    print("PDF REPORT TEST")
    print("=" * 60)

    from src.core.database import list_documents

    docs = list_documents(limit=1)
    if not docs:
        print("⚠️ No documents yet")
        print("   Upload some via the Streamlit app first")
    else:
        doc = docs[0]
        try:
            path = generate_pdf_report(doc['id'])
            print(f"✅ Report created: {path}")
            print(f"   Open with any PDF viewer")
        except Exception as e:
            print(f"❌ Error: {e}")