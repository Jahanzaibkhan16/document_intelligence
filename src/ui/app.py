# src/ui/app.py
"""Streamlit web UI for Document Intelligence System."""
import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.core.config import (
    UPLOADS_DIR, EXTRACTED_DIR, GEMINI_MODEL
)
from src.core.database import (
    init_db, add_document, update_document, get_document,
    list_documents, delete_document, get_stats, search_documents
)
from src.processing.extractors import extract_text
from src.processing.ai_extractor import process_document


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ================= INIT =================
init_db()


# ================= HELPERS =================
def render_field(label, value):
    """Render a field with proper formatting."""
    if value is None or value == "" or value == []:
        return

    st.markdown(f"**{label}:**")
    st.markdown(f"<div style='background:#f0f2f6; padding:8px 12px; border-radius:6px; margin-bottom:8px; color:#0f1419;'>{value}</div>",
                unsafe_allow_html=True)


def render_list_items(title, items):
    """Render a list of items (line items, education, etc.)."""
    if not items:
        return

    st.markdown(f"#### 📋 {title}")

    if isinstance(items, list):
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                with st.container():
                    st.markdown(f"**#{i}**")
                    for k, v in item.items():
                        if v is not None and v != "":
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**{k.replace('_', ' ').title()}:** {v}")
                    st.markdown("---")
            else:
                st.markdown(f"- {item}")
    else:
        st.markdown(f"{items}")


# ================= SIDEBAR =================
with st.sidebar:
    st.title("📄 Document AI")
    st.caption("Extract data from any document")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Upload & Extract", "📚 History", "🔍 Search",
         "📊 Statistics", "📤 Bulk Export"],
    )

    st.markdown("---")
    st.caption("**Supported:** PDF, JPG, PNG, DOCX, TXT")
    st.caption(f"**AI Model:** {GEMINI_MODEL}")


# ================= PAGE 1 — UPLOAD & EXTRACT =================
if page == "🏠 Upload & Extract":
    st.header("📄 Upload Document")
    st.caption("Drag & drop a file below, and AI will extract structured data.")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "png", "jpg", "jpeg", "docx", "txt"],
    )

    if uploaded_file is not None:
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = uploaded_file.name.replace(" ", "_")
        save_path = UPLOADS_DIR / f"{timestamp}_{safe_name}"

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # File info
        col1, col2, col3 = st.columns(3)
        col1.metric("Filename", uploaded_file.name[:25])
        col2.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        col3.metric("Type", Path(uploaded_file.name).suffix.upper())

        # Preview
        with st.expander("📎 Preview"):
            if uploaded_file.type.startswith("image"):
                st.image(uploaded_file, use_container_width=True)
            else:
                st.info(f"{uploaded_file.name} ready for extraction.")

        # Extract button
        if st.button("🚀 Extract with AI", type="primary",
                     use_container_width=True):

            with st.spinner("Processing..."):
                progress = st.progress(0)
                status = st.empty()

                try:
                    # Register
                    status.info("📝 Registering...")
                    doc_id = add_document(
                        filename=uploaded_file.name,
                        filepath=str(save_path),
                        file_size=uploaded_file.size,
                        file_type=Path(uploaded_file.name).suffix.lower(),
                    )
                    progress.progress(20)

                    # Extract text
                    status.info("📖 Reading document...")
                    text, method = extract_text(str(save_path))
                    progress.progress(40)

                    if not text or len(text) < 10:
                        update_document(doc_id, status="failed")
                        st.error("❌ Could not extract text.")
                    else:
                        # AI extraction
                        status.info("🤖 AI extraction...")
                        progress.progress(60)

                        ok, result = process_document(text)
                        progress.progress(100)

                        if not ok:
                            update_document(doc_id, raw_text=text,
                                             status="failed",
                                             error_message=str(result))
                            st.error(f"❌ AI failed: {result}")
                        else:
                            # Save
                            update_document(
                                doc_id,
                                doc_type=result['doc_type'],
                                raw_text=text,
                                extracted_json=json.dumps(
                                    result['fields'], ensure_ascii=False
                                ),
                                confidence=result['confidence'],
                                status="done",
                            )
                            status.success("✅ Done!")

                            st.success(
                                f"✅ Extracted **{result['doc_type'].upper()}** "
                                f"with **{result['confidence']*100:.0f}%** confidence"
                            )

                            st.markdown("---")
                            st.subheader("📊 Extracted Data")

                            fields = result['fields']

                            # Separate simple from complex
                            simple = {}
                            lists = {}
                            for k, v in fields.items():
                                if isinstance(v, list) and v:
                                    lists[k] = v
                                elif v is not None and v != "" and not isinstance(v, (list, dict)):
                                    simple[k] = v

                            # Display simple fields as 2-column markdown
                            if simple:
                                items = list(simple.items())
                                col_left, col_right = st.columns(2)

                                for i, (k, v) in enumerate(items):
                                    target = col_left if i % 2 == 0 else col_right
                                    with target:
                                        st.markdown(f"**{k.replace('_', ' ').title()}**")
                                        st.code(str(v), language=None)

                            # Display lists
                            for key, items in lists.items():
                                st.markdown("---")
                                render_list_items(
                                    key.replace('_', ' ').title(),
                                    items
                                )

                            # ============ EXPORTS ============
                            st.markdown("---")
                            st.subheader("📤 Download")

                            from src.processing.pdf_report import (
                                generate_pdf_report
                            )

                            col1, col2, col3, col4 = st.columns(4)

                            # JSON
                            with col1:
                                st.download_button(
                                    "📥 JSON",
                                    data=json.dumps(result, indent=2,
                                                     ensure_ascii=False),
                                    file_name=f"extraction_{doc_id}.json",
                                    mime="application/json",
                                    use_container_width=True,
                                )

                            # CSV
                            with col2:
                                import pandas as pd
                                df = pd.DataFrame([simple])
                                st.download_button(
                                    "📊 CSV",
                                    data=df.to_csv(index=False),
                                    file_name=f"extraction_{doc_id}.csv",
                                    mime="text/csv",
                                    use_container_width=True,
                                )

                            # PDF Report
                            with col3:
                                if st.button("📄 Generate PDF",
                                              use_container_width=True):
                                    try:
                                        pdf_path = generate_pdf_report(doc_id)
                                        with open(pdf_path, "rb") as f:
                                            st.download_button(
                                                "📄 Download PDF",
                                                data=f.read(),
                                                file_name=os.path.basename(pdf_path),
                                                mime="application/pdf",
                                                key=f"pdf_{doc_id}",
                                                use_container_width=True,
                                            )
                                    except Exception as e:
                                        st.error(f"PDF error: {e}")

                            # Excel — individual
                            with col4:
                                if st.button("📊 Generate Excel",
                                              use_container_width=True):
                                    try:
                                        from src.processing.excel_export import (
                                            export_to_excel
                                        )
                                        xlsx_path = export_to_excel([doc_id])
                                        with open(xlsx_path, "rb") as f:
                                            st.download_button(
                                                "📊 Download Excel",
                                                data=f.read(),
                                                file_name=os.path.basename(xlsx_path),
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                key=f"xlsx_{doc_id}",
                                                use_container_width=True,
                                            )
                                    except Exception as e:
                                        st.error(f"Excel error: {e}")

                            with st.expander("🔧 Raw JSON"):
                                st.json(result['fields'])

                except Exception as e:
                    st.error(f"❌ {e}")
                    st.exception(e)


# ================= PAGE 2 — HISTORY =================
elif page == "📚 History":
    st.header("📚 Document History")

    col1, col2 = st.columns([2, 1])
    with col1:
        doc_type_filter = st.selectbox(
            "Filter by type",
            ["all", "invoice", "receipt", "id_card", "resume",
             "bank_statement", "purchase_order", "business_card",
             "utility_bill"],
        )
    with col2:
        limit = st.number_input("Max results", 10, 500, 100)

    docs = list_documents(
        doc_type=None if doc_type_filter == "all" else doc_type_filter,
        limit=int(limit)
    )

    if not docs:
        st.info("📭 No documents yet.")
    else:
        st.caption(f"**Showing {len(docs)} documents**")

        for doc in docs:
            with st.expander(
                f"📄 {doc['filename']} — {doc['doc_type'] or 'unknown'} "
                f"({doc['status']})"
            ):
                col1, col2, col3 = st.columns(3)
                col1.metric("Type", doc['doc_type'] or "unknown")
                col2.metric("Status", doc['status'])
                col3.metric("Confidence",
                            f"{(doc['confidence'] or 0)*100:.0f}%")

                st.caption(f"Uploaded: {doc['uploaded_on']}")

                if doc.get('extracted_json'):
                    try:
                        fields = json.loads(doc['extracted_json'])
                        with st.expander("👁️ View extracted data"):
                            st.json(fields)
                    except Exception:
                        pass

                c1, c2 = st.columns(2)
                with c1:
                    if doc.get('extracted_json'):
                        st.download_button(
                            "📥 JSON",
                            data=doc['extracted_json'],
                            file_name=f"doc_{doc['id']}.json",
                            mime="application/json",
                            key=f"dl_{doc['id']}"
                        )
                with c2:
                    if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                        delete_document(doc['id'])
                        st.rerun()


# ================= PAGE 3 — SEARCH =================
elif page == "🔍 Search":
    st.header("🔍 Search Documents")

    query = st.text_input(
        "Search in filenames and extracted data",
        placeholder="e.g., 'Ahmed', 'INV-2025', 'Karachi'"
    )

    if query:
        results = search_documents(query)

        if not results:
            st.info(f"No results for '{query}'")
        else:
            st.caption(f"**Found {len(results)} matches**")

            for doc in results:
                with st.expander(f"📄 {doc['filename']} — {doc['doc_type']}"):
                    st.caption(f"Uploaded: {doc['uploaded_on']}")
                    if doc.get('extracted_json'):
                        try:
                            st.json(json.loads(doc['extracted_json']))
                        except Exception:
                            pass


# ================= PAGE 4 — STATISTICS =================
elif page == "📊 Statistics":
    st.header("📊 Dashboard")

    stats = get_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Total", stats['total'])
    c2.metric("✅ Processed", stats['by_status'].get('done', 0))
    c3.metric("⏳ Pending", stats['by_status'].get('pending', 0))
    c4.metric("❌ Failed", stats['by_status'].get('failed', 0))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 By Type")
        if stats['by_type']:
            import pandas as pd
            df = pd.DataFrame(
                list(stats['by_type'].items()),
                columns=['Type', 'Count']
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(df.set_index('Type'))
        else:
            st.info("No data yet")

    with col2:
        st.subheader("📊 By Status")
        if stats['by_status']:
            import pandas as pd
            df = pd.DataFrame(
                list(stats['by_status'].items()),
                columns=['Status', 'Count']
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No data yet")

    st.markdown("---")
    st.subheader("💾 Recent Documents")
    recent = list_documents(limit=10)
    if recent:
        import pandas as pd
        df = pd.DataFrame([{
            'ID': d['id'],
            'Filename': d['filename'],
            'Type': d['doc_type'] or '-',
            'Status': d['status'],
            'Confidence': f"{(d['confidence'] or 0)*100:.0f}%",
            'Uploaded': d['uploaded_on'],
        } for d in recent])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No documents yet")

# ================= PAGE 5 — BULK EXPORT =================
elif page == "📤 Bulk Export":
    st.header("📤 Bulk Export")
    st.caption("Export multiple documents at once to Excel or PDF.")

    # Fetch all documents
    all_docs = list_documents(limit=10000)

    if not all_docs:
        st.info("📭 No documents to export. Upload some first.")
    else:
        st.markdown(f"**Total documents available:** {len(all_docs)}")

        # Filter options
        col1, col2 = st.columns(2)

        with col1:
            filter_type = st.selectbox(
                "Filter by type",
                ["all", "invoice", "receipt", "id_card", "resume"],
            )

        with col2:
            only_done = st.checkbox("Only processed documents",
                                     value=True)

        # Filter docs
        filtered = all_docs
        if filter_type != "all":
            filtered = [d for d in filtered if d['doc_type'] == filter_type]
        if only_done:
            filtered = [d for d in filtered if d['status'] == 'done']

        st.markdown(f"**Selected: {len(filtered)} documents**")

        if filtered:
            # Preview table
            import pandas as pd
            preview_df = pd.DataFrame([{
                'ID': d['id'],
                'Filename': d['filename'],
                'Type': d['doc_type'] or '-',
                'Confidence': f"{(d['confidence'] or 0)*100:.0f}%",
            } for d in filtered])
            st.dataframe(preview_df, use_container_width=True,
                          hide_index=True)

            st.markdown("---")

            # Export buttons
            st.subheader("Choose export format")

            col1, col2 = st.columns(2)

            # ============ EXCEL BULK ============
            with col1:
                st.markdown("### 📊 Excel Workbook")
                st.caption("One workbook with all documents, line items, "
                           "and summary sheets.")

                if st.button("📊 Generate Excel", key="bulk_excel",
                              type="primary", use_container_width=True):
                    with st.spinner(f"Building Excel ({len(filtered)} docs)..."):
                        try:
                            from src.processing.excel_export import (
                                export_to_excel
                            )
                            doc_ids = [d['id'] for d in filtered]
                            xlsx_path = export_to_excel(doc_ids)

                            with open(xlsx_path, "rb") as f:
                                st.download_button(
                                    "📥 Download Excel",
                                    data=f.read(),
                                    file_name=os.path.basename(xlsx_path),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="dl_bulk_excel",
                                    use_container_width=True,
                                )
                            st.success(f"✅ Excel ready: {os.path.basename(xlsx_path)}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

            # ============ PDF BULK (ZIP) ============
            with col2:
                st.markdown("### 📄 PDF Reports (ZIP)")
                st.caption("One PDF per document, all zipped together.")

                if st.button("📄 Generate PDFs", key="bulk_pdf",
                              type="primary", use_container_width=True):
                    with st.spinner(f"Generating PDFs ({len(filtered)} docs)..."):
                        try:
                            import zipfile
                            import io
                            from src.processing.pdf_report import (
                                generate_pdf_report
                            )

                            zip_buffer = io.BytesIO()

                            with zipfile.ZipFile(zip_buffer, 'w',
                                                  zipfile.ZIP_DEFLATED) as zf:
                                for i, doc in enumerate(filtered, 1):
                                    try:
                                        pdf_path = generate_pdf_report(doc['id'])
                                        zf.write(pdf_path,
                                                 arcname=os.path.basename(pdf_path))
                                    except Exception as e:
                                        print(f"Failed for doc {doc['id']}: {e}")

                            zip_buffer.seek(0)

                            st.download_button(
                                "📥 Download ZIP",
                                data=zip_buffer.getvalue(),
                                file_name=f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip",
                                key="dl_bulk_pdf",
                                use_container_width=True,
                            )
                            st.success(f"✅ ZIP ready with {len(filtered)} reports")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ No documents match your filter.")