import time
import os
import litellm
from app.core.config import settings

os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
litellm.suppress_debug_info = True

# Test 1: gemini-3-flash-preview with thinking config or max_tokens
t0 = time.time()
try:
    res = litellm.completion(
        model="gemini/gemini-3-flash-preview",
        messages=[{"role": "user", "content": "hello"}],
        extra_body={"generationConfig": {"thinkingConfig": {"thinkingBudget": 0}}}
    )
    print("Test 1 (thinkingBudget=0):", round(time.time() - t0, 2), "s ->", res.choices[0].message.content)
except Exception as e:
    print("Test 1 failed:", e)

# Test 2: gemini-2.5-flash vs gemini-2.5-flash-preview
t0 = time.time()
try:
    res = litellm.completion(
        model="gemini/gemini-2.5-flash-preview",
        messages=[{"role": "user", "content": "hello"}],
    )
    print("Test 2 (gemini-2.5-flash-preview):", round(time.time() - t0, 2), "s ->", res.choices[0].message.content)
except Exception as e:
    print("Test 2 failed:", e)
