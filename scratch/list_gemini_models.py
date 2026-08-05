import os
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
for m in models:
    print(m)
