import sys
import json
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from app.main import app
from app.api.v1.deps import get_dense_retriever, get_chat_service
from app.retriever.base import BaseRetriever
from app.retriever.sparse import SparseBM25Retriever
from app.services.chat_service import ChatService

# Ensure UTF-8 stdout
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore


class MockDenseRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int = 5):
        return [Document(page_content="Mock knowledge context for isolated unit testing.")]


def test_streaming():
    """Verify chat stream endpoint returns SSE events in CI and local environments."""
    mock_dense = MockDenseRetriever()
    sparse = SparseBM25Retriever([Document(page_content="Mock knowledge context.")])
    app.dependency_overrides[get_dense_retriever] = lambda: mock_dense
    app.dependency_overrides[get_chat_service] = lambda: ChatService(mock_dense, sparse)

    try:
        client = TestClient(app)
        payload = {"question": "Hello, how are you today?"}
        with client.stream("POST", "/api/v1/chat/stream", json=payload) as r:
            assert r.status_code == 200
            event_types = []
            for line in r.iter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        ev_type = data.get("type")
                        if ev_type:
                            event_types.append(ev_type)
                    except Exception:
                        pass
            # Should at least receive step and done/token/metadata events
            assert len(event_types) > 0
    finally:
        app.dependency_overrides.clear()


if __name__ == "__main__":
    test_streaming()

