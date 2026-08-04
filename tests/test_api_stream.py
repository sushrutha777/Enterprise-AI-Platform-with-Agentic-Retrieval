import sys
import json
from fastapi.testclient import TestClient
from app.main import app

# Ensure UTF-8 stdout
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

client = TestClient(app)


def test_streaming():
    """Verify chat stream endpoint returns SSE events."""
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


if __name__ == "__main__":
    test_streaming()
