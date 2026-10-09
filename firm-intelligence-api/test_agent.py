# 1. Set up some fake building blocks
# 2. Create a fake model (that keeps going)
# 3. Sub in our fakes from step 1
# 4. Hit our endpoint
# 5. Check it stopped
#
# Pretend the model never stops - check your code stops it anyway

from fastapi.testclient import TestClient

import agent
from main import app

client = TestClient(app)


class FakeToolUseBlock:
    type = "tool_use"
    id = "toolu_01"
    name = "search_knowledge_base"

    def __init__(self, input_):
        self.input = input_


class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens = i
        self.output_tokens = o


class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content = content
        self.stop_reason = stop_reason
        self.usage = usage


def test_agent_stops_at_max_iterations_instead_of_looping_forever(monkeypatch):

    def fake_create(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query": "anything"})],
            "tool_use",
            FakeUsage(100, 15),
        )

    monkeypatch.setattr(
        agent.client.messages,
        "create",
        fake_create,
    )

    monkeypatch.setattr(
        agent.knowledge,
        "search",
        lambda q, top_k=3: [
            {
                "id": "doc-001",
                "title": "t",
                "text": "x",
                "score": 0.5,
            }
        ],
    )

    response = client.post(
        "/agent/ask",
        json={"question": "never resolves"},
    )

    body = response.json()

    # Check the endpoint completed successfully
    assert response.status_code == 200

    # Check our safety limit stopped the loop
    assert body["stop_reason"] == "max_iterations"

    # Fake model returned one tool call per iteration
    assert body["tool_calls_made"] == agent.MAX_ITERATIONS