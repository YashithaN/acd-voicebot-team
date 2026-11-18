"""Deterministic mock reasoning for W3."""

from .schemas import ReasoningRequest, ReasoningResult
from .validation import validate_request, validate_result


def run_mock_reasoning(request: ReasoningRequest) -> ReasoningResult:
    """Return a predictable answer using only the supplied context."""

    validate_request(request)

    question = request.question.lower()
    items = request.context.items

    if not items:
        answer = "No context items are available to answer the question."
        grounded_item_ids = []
        confidence = 0.0
    else:
        # Deterministic mock behavior: summarize the supplied context.
        summary = "; ".join(item.content for item in items)
        answer = f"Mock answer based on the available context: {summary}"
        grounded_item_ids = [item.item_id for item in items]
        confidence = 0.9

    result = ReasoningResult(
        request_id=request.request_id,
        answer=answer,
        grounded_item_ids=grounded_item_ids,
        confidence=confidence,
        prompt_version=request.prompt_version,
        mode="mock",
    )

    return validate_result(request, result)