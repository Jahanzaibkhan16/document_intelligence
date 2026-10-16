# src/core/config.py
"""Central configuration — loads .env and defines paths."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (for local development)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Try to load Streamlit secrets (for cloud deployment)
_STREAMLIT_SECRETS = {}
try:
    import streamlit as st
    _STREAMLIT_SECRETS = dict(st.secrets)
except Exception:
    pass


def _get_setting(key, default=""):
    """Get a setting from .env or Streamlit secrets."""
    # Try Streamlit secrets first (cloud)
    if key in _STREAMLIT_SECRETS:
        return _STREAMLIT_SECRETS[key]
    # Fall back to environment variables (.env)
    return os.getenv(key, default)


# ================= PATHS =================
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
EXTRACTED_DIR = DATA_DIR / "extracted"
SAMPLES_DIR = DATA_DIR / "samples"
DB_PATH = DATA_DIR / "documents.db"

# Ensure folders exist
for d in [DATA_DIR, UPLOADS_DIR, EXTRACTED_DIR, SAMPLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ================= GEMINI API =================
GEMINI_API_KEY = _get_setting("GEMINI_API_KEY", "")
GEMINI_MODEL = _get_setting("GEMINI_MODEL", "gemini-flash-latest")


# ================= TESSERACT =================
# Tesseract path — different on Windows vs Linux (cloud)
_default_tesseract = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.name == "nt"
    else "/usr/bin/tesseract"
)
TESSERACT_CMD = _get_setting("TESSERACT_CMD", _default_tesseract)


# ================= APP SETTINGS =================
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))

SUPPORTED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg",
    ".docx", ".doc", ".tiff", ".bmp"
}

DOCUMENT_TYPES = [
    "invoice", "receipt", "id_card", "resume", "unknown"
]

COLOR_BG       = "#0f1419"
COLOR_PANEL    = "#1a2332"
COLOR_PANEL_2  = "#232f42"
COLOR_ACCENT   = "#00d4aa"
COLOR_DANGER   = "#e74c3c"
COLOR_INFO     = "#3498db"
COLOR_WARN     = "#f39c12"
COLOR_SUCCESS  = "#26a69a"
COLOR_TEXT     = "#ecf0f1"
COLOR_TEXT_DIM = "#7f8c8d"