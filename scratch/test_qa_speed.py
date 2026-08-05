import time
import os
import litellm
from app.core.config import settings

os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
litellm.suppress_debug_info = True

t0 = time.time()
res = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "According to the FAQ, what are the payment methods? (Context: Credit cards, UPI, net banking, COD)"}
    ],
)
elapsed = round(time.time() - t0, 2)
print(f"Time: {elapsed}s")
print(f"Answer: {res.choices[0].message.content}")
