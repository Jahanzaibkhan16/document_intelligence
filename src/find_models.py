# src/find_models.py
"""List all available Gemini models for your API key."""
import requests

from src.core.config import GEMINI_API_KEY


print("=" * 60)
print("AVAILABLE GEMINI MODELS")
print("=" * 60)
print()

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set")
    exit()

url = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models?key={GEMINI_API_KEY}"
)

try:
    r = requests.get(url, timeout=30)

    if r.status_code != 200:
        print(f"❌ HTTP {r.status_code}: {r.text[:200]}")
        exit()

    data = r.json()

    if 'models' not in data:
        print("❌ No models in response")
        print(r.text[:500])
        exit()

    print(f"Found {len(data['models'])} models:\n")

    for model in data['models']:
        name = model.get('name', '')
        methods = model.get('supportedGenerationMethods', [])

        # Only show models that support generateContent
        if 'generateContent' in methods:
            display = name.replace('models/', '')
            print(f"  ✅ {display}")

except Exception as e:
    print(f"❌ Error: {e}")