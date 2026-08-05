import time
import os
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

for model_name in all_models:
    try:
        model = genai.GenerativeModel(model_name)
        t0 = time.time()
        response = model.generate_content("hello")
        elapsed = round(time.time() - t0, 2)
        txt = response.text.strip().replace("\n", " ")[:40]
        print(f"SUCCESS: {model_name:35} in {elapsed:5.2f}s -> {txt}")
    except Exception as e:
        err_msg = str(e).split("\n")[0][:60]
        print(f"FAILED:  {model_name:35} -> {err_msg}")
