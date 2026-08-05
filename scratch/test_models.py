import time
import os
import litellm
from app.core.config import settings

os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
litellm.suppress_debug_info = True

candidates = [
    "gemini/gemini-2.0-flash",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-1.5-flash",
    "gemini/gemini-3-flash-preview",
]

for model in candidates:
    t0 = time.time()
    try:
        res = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "hello"}],
        )
        elapsed = round(time.time() - t0, 2)
        content = res.choices[0].message.content.strip().replace("\n", " ")
        print(f"✅ {model}: {elapsed}s -> {content[:50]}")
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        print(f"❌ {model}: {elapsed}s -> Error: {e}")
