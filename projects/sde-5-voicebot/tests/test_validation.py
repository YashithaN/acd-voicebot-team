import pytest

from context_reasoning.schemas import ReasoningRequest, ReasoningResult
from context_reasoning.synthetic_frames import create_sample_context
from context_reasoning.validation import validate_request, validate_result


def make_request():
    return ReasoningRequest(
        request_id="test-001",
        question="What is the project status?",
        context=create_sample_context(),
    )


def test_valid_request_accepted():
    request = make_request()
    assert validate_request(request) == request


def test_capture_must_remain_disabled():
    request = make_request()
    assert request.context.capture_enabled is False


def test_valid_result_accepted():
    request = make_request()
    result = ReasoningResult(
        request_id=request.request_id,
        answer="The project is in progress.",
        grounded_item_ids=["item-003"],
        confidence=0.9,
        prompt_version=request.prompt_version,
        mode="mock",
    )
    assert validate_result(request, result) == result


def test_result_with_wrong_request_id_rejected():
    request = make_request()
    result = ReasoningResult(
        request_id="different-id",
        answer="Mock answer",
        grounded_item_ids=[],
        confidence=0.5,
        prompt_version=request.prompt_version,
        mode="mock",
    )
    with pytest.raises(ValueError, match="request_id"):
        validate_result(request, result)


def test_unknown_grounded_item_rejected():
    request = make_request()
    result = ReasoningResult(
        request_id=request.request_id,
        answer="Mock answer",
        grounded_item_ids=["unknown-item"],
        confidence=0.5,
        prompt_version=request.prompt_version,
        mode="mock",
    )
    with pytest.raises(ValueError, match="unknown context item"):
        validate_result(request, result)