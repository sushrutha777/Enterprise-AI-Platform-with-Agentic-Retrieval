import time
import os
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

test_models = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
]

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        t0 = time.time()
        response = model.generate_content("hello")
        elapsed = round(time.time() - t0, 2)
        print(f"✅ {model_name:30} in {elapsed:5.2f}s -> {response.text.strip()[:40]}")
    except Exception as e:
        print(f"❌ {model_name:30} failed: {e}")
