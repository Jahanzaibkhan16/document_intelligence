# test_setup.py — verify the entire project setup
import os
import sys


print("=" * 60)
print("PROJECT SETUP TEST")
print("=" * 60)
print(f"Python: {sys.version.split()[0]}")
print()

# 1. Test imports
print("Testing imports:")
try:
    from src.core.config import (
        DATA_DIR, DB_PATH, GEMINI_API_KEY,
        TESSERACT_CMD, SUPPORTED_EXTENSIONS
    )
    print(f"  ✅ src.core.config imported")
except Exception as e:
    print(f"  ❌ src.core.config failed: {e}")
    sys.exit(1)

try:
    from src.core.database import init_db
    print(f"  ✅ src.core.database imported")
except Exception as e:
    print(f"  ❌ src.core.database failed: {e}")

try:
    from src.processing.extractors import extract_text
    print(f"  ✅ src.processing.extractors imported")
except Exception as e:
    print(f"  ❌ src.processing.extractors failed: {e}")

print()
print("Config values:")
print(f"  DATA_DIR:      {DATA_DIR}")
print(f"  DB_PATH:       {DB_PATH}")
print(f"  GEMINI key:    {'✅ set' if GEMINI_API_KEY else '❌ MISSING'}")
print(f"  Tesseract:     {TESSERACT_CMD}")
print(f"  Tesseract OK:  {os.path.exists(TESSERACT_CMD)}")
print(f"  Supported:     {sorted(SUPPORTED_EXTENSIONS)}")

print()
print("Testing database:")
try:
    init_db()
    print(f"  ✅ Database ready")
except Exception as e:
    print(f"  ❌ Database failed: {e}")

print()
print("=" * 60)
print("✅ Setup complete!" if GEMINI_API_KEY else "⚠️ Add GEMINI_API_KEY to .env")
print("=" * 60)