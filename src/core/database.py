# src/core/database.py
"""SQLite database layer for document storage."""
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.core.config import DB_PATH


# ================= CONNECTION =================
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INIT =================
def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                doc_type TEXT,
                raw_text TEXT,
                extracted_json TEXT,
                confidence REAL,
                ai_model TEXT,
                uploaded_on TEXT NOT NULL,
                processed_on TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                field_value TEXT,
                field_type TEXT,
                confidence REAL,
                FOREIGN KEY(document_id) REFERENCES documents(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_docs_type
            ON documents(doc_type)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_docs_date
            ON documents(uploaded_on DESC)
        """)

        conn.commit()
    print("✅ Database initialized")


# ================= DOCUMENT CRUD =================
def add_document(filename, filepath, file_size, file_type):
    """Insert a new document, return its ID."""
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO documents
            (filename, filepath, file_size, file_type,
             uploaded_on, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (filename, filepath, file_size, file_type,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return cur.lastrowid


def update_document(doc_id, **fields):
    """Update any fields on a document."""
    if not fields:
        return

    allowed = {
        'doc_type', 'raw_text', 'extracted_json', 'confidence',
        'ai_model', 'processed_on', 'status', 'error_message'
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [doc_id]

    with get_conn() as conn:
        conn.execute(f"UPDATE documents SET {set_clause} WHERE id = ?",
                     values)
        conn.commit()


def get_document(doc_id):
    """Fetch one document by ID."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
        return dict(row) if row else None


def list_documents(doc_type=None, limit=100, offset=0):
    """List documents, optionally filtered by type."""
    with get_conn() as conn:
        if doc_type and doc_type != "all":
            rows = conn.execute("""
                SELECT * FROM documents
                WHERE doc_type = ?
                ORDER BY uploaded_on DESC
                LIMIT ? OFFSET ?
            """, (doc_type, limit, offset)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM documents
                ORDER BY uploaded_on DESC
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]


def search_documents(query, limit=50):
    """Full-text search in extracted JSON, filename, raw text."""
    if not query:
        return []

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM documents
            WHERE extracted_json LIKE ?
               OR filename LIKE ?
               OR raw_text LIKE ?
            ORDER BY uploaded_on DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
        return [dict(r) for r in rows]


def delete_document(doc_id):
    """Delete a document and its extractions."""
    with get_conn() as conn:
        conn.execute("DELETE FROM extractions WHERE document_id = ?",
                     (doc_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()


# ================= EXTRACTIONS =================
def save_extractions(doc_id, fields):
    """Store individual extracted fields (optional — for search)."""
    with get_conn() as conn:
        conn.execute("DELETE FROM extractions WHERE document_id = ?",
                     (doc_id,))
        for key, value in fields.items():
            if value is None:
                continue

            if isinstance(value, (list, dict)):
                value_str = json.dumps(value, ensure_ascii=False)
                value_type = type(value).__name__
            else:
                value_str = str(value)
                value_type = type(value).__name__

            conn.execute("""
                INSERT INTO extractions
                (document_id, field_name, field_value, field_type)
                VALUES (?, ?, ?, ?)
            """, (doc_id, key, value_str, value_type))
        conn.commit()


def get_extractions(doc_id):
    """Get all extracted fields for a document."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT field_name, field_value, field_type
            FROM extractions
            WHERE document_id = ?
        """, (doc_id,)).fetchall()
        return [dict(r) for r in rows]


# ================= STATS =================
def get_stats():
    """Get dashboard statistics."""
    with get_conn() as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM documents"
        ).fetchone()['c']

        by_type = conn.execute("""
            SELECT doc_type, COUNT(*) AS c
            FROM documents
            WHERE doc_type IS NOT NULL
            GROUP BY doc_type
        """).fetchall()

        by_status = conn.execute("""
            SELECT status, COUNT(*) AS c
            FROM documents
            GROUP BY status
        """).fetchall()

        return {
            'total': total,
            'by_type': {r['doc_type']: r['c'] for r in by_type},
            'by_status': {r['status']: r['c'] for r in by_status},
        }


# ================= MAIN =================
if __name__ == "__main__":
    init_db()

    # Quick test
    doc_id = add_document(
        filename="test.pdf",
        filepath="/tmp/test.pdf",
        file_size=12345,
        file_type=".pdf",
    )
    print(f"✅ Inserted document ID: {doc_id}")

    doc = get_document(doc_id)
    print(f"✅ Fetched: {doc['filename']}")

    update_document(doc_id, doc_type="invoice", status="done")
    doc = get_document(doc_id)
    print(f"✅ Updated: {doc['doc_type']} / {doc['status']}")

    delete_document(doc_id)
    print(f"✅ Cleaned up test document")

    print(f"\nStats: {get_stats()}")