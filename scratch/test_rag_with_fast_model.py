import time
import os
import litellm
from app.core.config import settings

os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
litellm.suppress_debug_info = True

fast_model = "gemini/gemini-3.1-flash-lite"
rag_context = """
[FAQ]
Q: What is the return policy?
A: You can return items within 30 days of delivery for a full refund. Items must be unused and in original packaging.

Q: What payment methods are accepted?
A: We accept Visa, Mastercard, American Express, PayPal, Apple Pay, and COD (Cash on Delivery).
"""

question = "What payment methods can I use and how many days do I have to return an item?"

prompt = f"""You are a helpful customer support agent. Answer the question accurately using the provided context.

Context:
{rag_context}

Question: {question}

Answer:"""

t0 = time.time()
res = litellm.completion(
    model=fast_model,
    messages=[{"role": "user", "content": prompt}],
)
elapsed = round(time.time() - t0, 2)

print(f"Model: {fast_model}")
print(f"Time:  {elapsed}s")
print(f"Answer:\n{res.choices[0].message.content}")
