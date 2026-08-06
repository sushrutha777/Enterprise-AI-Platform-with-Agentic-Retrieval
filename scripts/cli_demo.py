"""Interactive CLI Demonstration Script for Enterprise Agentic RAG Platform."""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from app.core.config import settings
from app.api.v1.deps import get_chat_service
from app.schemas.chat import ChatRequest


async def ask_question(question: str, conversation_id: str = "cli_demo_session"):
    """Send a question to the Agentic RAG chat pipeline and display the step-by-step reasoning."""
    print("\n" + "=" * 80)
    print(f"🔹 QUESTION: {question}")
    print("=" * 80)

    # Check for API key
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY.startswith("your_"):
        print("\n⚠️  NOTE: GOOGLE_API_KEY is not set or is still a placeholder in .env.")
        print("   To get live LLM answers from Gemini, add your key to `.env`:")
        print("   GOOGLE_API_KEY=AIzaSy...\n")

    chat_service = get_chat_service()
    req = ChatRequest(question=question, conversation_id=conversation_id)

    answer_tokens = []
    metadata = {}
    
    print("\n🔄 Execution Pipeline:")
    async for sse_chunk in chat_service.stream_chat(req):
        for line in sse_chunk.split("\n"):
            if line.startswith("data: "):
                try:
                    payload = json.loads(line[6:])
                    ev_type = payload.get("type")

                    if ev_type == "step":
                        print(f"  ⚡ [STEP] {payload.get('label')}")
                    elif ev_type == "metadata":
                        metadata = payload
                        intent = payload.get("intent", "unknown")
                        tools = payload.get("tool_used", "none")
                        rewritten = payload.get("rewritten_query")
                        print(f"  🎯 [ROUTING] Intent: {intent.upper()} | Tool(s) used: {tools}")
                        if rewritten and rewritten != question:
                            print(f"  📝 [CONTEXT REWRITE] {rewritten}")
                    elif ev_type == "token":
                        answer_tokens.append(payload.get("token", ""))
                    elif ev_type == "done":
                        latency = payload.get("latency_seconds")
                        print(f"  ⏱️ [DONE] Response generated in {latency}s")
                    elif ev_type == "error":
                        print(f"  ❌ [ERROR] {payload.get('error')}")
                except Exception:
                    pass

    print("\n💬 AGENT RESPONSE:")
    print("-" * 80)
    full_answer = "".join(answer_tokens).strip()
    if full_answer:
        print(full_answer)
    else:
        print("(No text generated - please check API key or error message above)")
    print("-" * 80)

    # Display Sources if retrieved
    sources = metadata.get("sources", [])
    if sources:
        print(f"\n📚 RETRIEVED SOURCES ({len(sources)}):")
        for idx, src in enumerate(sources[:3], 1):
            title = src.get("title") or src.get("source") or "Document"
            url = src.get("url") or "Local Document"
            snippet = (src.get("content") or "")[:150].replace("\n", " ")
            print(f"  [{idx}] {title}")
            print(f"      Source: {url}")
            if snippet:
                print(f"      Excerpt: {snippet}...")


async def run_predefined_tests():
    """Runs a suite of sample questions across different agent intents."""
    print("\n" + "#" * 80)
    print("🚀 RUNNING AGENTIC RAG QUESTION-ANSWERING DEMO")
    print("#" * 80)

    suite = [
        ("Hi there! What can you help me with?", "session_test_1"),
        ("Who was Nikola Tesla and what did he invent?", "session_test_2"),
        ("What were some of his other inventions?", "session_test_2"),  # Multi-turn pronoun test
        ("What is the latest status of artificial intelligence in 2026?", "session_test_3"),
    ]

    for q, session in suite:
        await ask_question(q, conversation_id=session)


async def interactive_mode():
    """Allows user to enter arbitrary questions in the terminal."""
    session_id = "cli_interactive_session"
    print("\n" + "=" * 80)
    print("💡 INTERACTIVE QUESTION-ANSWERING MODE (Type 'exit' or 'quit' to stop)")
    print("=" * 80)

    while True:
        try:
            user_input = input("\nAsk a question: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting interactive test. Goodbye!")
                break
            await ask_question(user_input, conversation_id=session_id)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting interactive test.")
            break


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    elif len(sys.argv) > 1:
        # Run single question passed in CLI args
        question = " ".join(sys.argv[1:])
        asyncio.run(ask_question(question))
    else:
        asyncio.run(run_predefined_tests())


if __name__ == "__main__":
    main()
