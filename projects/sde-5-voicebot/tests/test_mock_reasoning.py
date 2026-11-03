import pytest

from context_reasoning.schemas import ReasoningRequest
from context_reasoning.synthetic_frames import create_sample_context
from context_reasoning.mock_reasoning import run_mock_reasoning


def make_request():
    return ReasoningRequest(
        request_id="mock-test-001",
        question="What is the project status?",
        context=create_sample_context(),
    )


def test_mock_reasoning_returns_result():
    result = run_mock_reasoning(make_request())

    assert result.request_id == "mock-test-001"
    assert result.mode == "mock"
    assert result.prompt_version == "v1"
    assert result.answer


def test_mock_reasoning_is_deterministic():
    request = make_request()

    first = run_mock_reasoning(request)
    second = run_mock_reasoning(request)

    assert first.answer == second.answer
    assert first.grounded_item_ids == second.grounded_item_ids
    assert first.confidence == second.confidence


def test_mock_reasoning_grounds_answer_in_context():
    result = run_mock_reasoning(make_request())

    assert result.grounded_item_ids
    assert set(result.grounded_item_ids) == {
        "item-001",
        "item-002",
        "item-003",
    }


def test_empty_context_returns_no_context_answer():
    request = ReasoningRequest(
        request_id="empty-test-001",
        question="What is shown?",
        context=create_sample_context().model_copy(update={"items": []}),
    )

    result = run_mock_reasoning(request)

    assert result.grounded_item_ids == []
    assert result.confidence == 0.0
    assert "No context items" in result.answer