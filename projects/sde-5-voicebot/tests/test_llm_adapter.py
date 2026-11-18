"""Tests for the provider-free LLM client adapter."""

import json

import pytest

from context_reasoning.llm_adapter import LLMAdapter, LLMAdapterError
from context_reasoning.schemas import ReasoningRequest
from context_reasoning.synthetic_frames import create_sample_context


def make_request():
    return ReasoningRequest(
        request_id="llm-test-001",
        question="What is the project status?",
        context=create_sample_context(),
    )


class SequenceClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def generate(self, request, timeout_seconds):
        self.calls.append((request, timeout_seconds))
        output = self.outputs.pop(0)
        if isinstance(output, BaseException):
            raise output
        return output


def valid_output(request):
    return {
        "request_id": request.request_id,
        "answer": "The project is in progress.",
        "grounded_item_ids": ["item-003"],
        "confidence": 0.9,
        "prompt_version": request.prompt_version,
        "mode": "mock",
    }


def test_mock_client_is_the_default_and_needs_no_credentials():
    result = LLMAdapter().complete(make_request())

    assert result.mode == "mock"
    assert result.grounded_item_ids


def test_timeout_is_passed_to_client_and_transient_failures_are_retried():
    request = make_request()
    client = SequenceClient([TimeoutError("temporary"), valid_output(request)])
    adapter = LLMAdapter(client, timeout_seconds=1.25, max_retries=1)

    result = adapter.complete(request)

    assert result.request_id == request.request_id
    assert len(client.calls) == 2
    assert all(call[1] == 1.25 for call in client.calls)


def test_retry_count_is_bounded():
    client = SequenceClient([TimeoutError("first"), TimeoutError("second")])
    adapter = LLMAdapter(client, max_retries=1)

    with pytest.raises(LLMAdapterError, match="configured retries"):
        adapter.complete(make_request())

    assert len(client.calls) == 2


def test_malformed_json_is_rejected():
    adapter = LLMAdapter(SequenceClient(["not valid json"]))

    with pytest.raises(LLMAdapterError, match="malformed JSON"):
        adapter.complete(make_request())


def test_invalid_structured_output_is_rejected():
    request = make_request()
    output = valid_output(request)
    output["confidence"] = 2.0
    adapter = LLMAdapter(SequenceClient([output]))

    with pytest.raises(LLMAdapterError, match="invalid or unsafe"):
        adapter.complete(request)


def test_unknown_grounding_is_rejected():
    request = make_request()
    output = valid_output(request)
    output["grounded_item_ids"] = ["not-in-context"]
    adapter = LLMAdapter(SequenceClient([output]))

    with pytest.raises(LLMAdapterError, match="invalid or unsafe"):
        adapter.complete(request)


def test_unsafe_capture_claim_field_is_rejected():
    request = make_request()
    output = valid_output(request)
    output["capture_enabled"] = True
    adapter = LLMAdapter(SequenceClient([json.dumps(output)]))

    with pytest.raises(LLMAdapterError, match="invalid or unsafe"):
        adapter.complete(request)