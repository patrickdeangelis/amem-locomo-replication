import json
import sys
from types import SimpleNamespace

import pytest

import memory_layer_robust
from memory_layer_robust import RobustOpenAIController


class FakeCompletions:
    def __init__(self, outcomes):
        self._outcomes = iter(outcomes)

    def create(self, **_kwargs):
        outcome = next(self._outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeOpenAI:
    outcomes = []

    def __init__(self, api_key):
        assert api_key == "test-key"
        self.chat = SimpleNamespace(completions=FakeCompletions(self.outcomes))


def response(content="answer", usage=None, model="gpt-4o-mini-2024-07-18"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=usage,
        model=model,
    )


def usage(input_tokens, cached_tokens, output_tokens, total_tokens):
    return SimpleNamespace(
        prompt_tokens=input_tokens,
        prompt_tokens_details=SimpleNamespace(cached_tokens=cached_tokens),
        completion_tokens=output_tokens,
        total_tokens=total_tokens,
    )


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    FakeOpenAI.outcomes = []
    return RobustOpenAIController(model="gpt-4o-mini", api_key="test-key")


def test_completed_calls_accumulate_a_serializable_usage_snapshot(controller):
    FakeOpenAI.outcomes = [
        response(usage=usage(100, 25, 10, 110)),
        response(usage=usage(80, 5, 20, 100)),
    ]
    controller.client.chat.completions = FakeCompletions(FakeOpenAI.outcomes)

    assert controller.get_completion("first secret prompt") == "answer"
    assert controller.get_completion("second secret prompt") == "answer"

    snapshot = controller.get_usage_snapshot()
    assert snapshot == {
        "requests": 2,
        "attempts_total": 2,
        "failed_attempts": 0,
        "input_tokens": 180,
        "cached_input_tokens": 30,
        "output_tokens": 30,
        "total_tokens": 210,
        "model": "gpt-4o-mini",
    }
    assert json.loads(json.dumps(snapshot)) == snapshot
    assert "prompt" not in snapshot


def test_completed_call_without_usage_counts_request_and_zero_tokens(controller):
    FakeOpenAI.outcomes = [response(usage=None)] * 3
    controller.client.chat.completions = FakeCompletions(FakeOpenAI.outcomes)

    assert controller.get_completion("secret prompt") == "answer"
    assert controller.get_usage_snapshot() == {
        "requests": 1,
        "attempts_total": 1,
        "failed_attempts": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model": "gpt-4o-mini",
    }


def test_reset_usage_clears_counts_without_changing_model(controller):
    FakeOpenAI.outcomes = [response(usage=usage(100, 25, 10, 110))]
    controller.client.chat.completions = FakeCompletions(FakeOpenAI.outcomes)
    controller.get_completion("secret prompt")

    controller.reset_usage()

    assert controller.get_usage_snapshot() == {
        "requests": 0,
        "attempts_total": 0,
        "failed_attempts": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model": "gpt-4o-mini",
    }


def test_failed_retry_is_not_counted_as_completed_usage(controller, monkeypatch):
    FakeOpenAI.outcomes = [
        RuntimeError("temporary failure"),
        response(usage=usage(40, 0, 8, 48)),
    ]
    controller.client.chat.completions = FakeCompletions(FakeOpenAI.outcomes)
    monkeypatch.setattr(memory_layer_robust.time, "sleep", lambda _delay: None)

    assert controller.get_completion("secret prompt") == "answer"
    assert controller.get_usage_snapshot() == {
        "requests": 1,
        "attempts_total": 2,
        "failed_attempts": 1,
        "input_tokens": 40,
        "cached_input_tokens": 0,
        "output_tokens": 8,
        "total_tokens": 48,
        "model": "gpt-4o-mini",
    }
