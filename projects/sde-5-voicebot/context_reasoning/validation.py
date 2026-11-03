
"""Validation helpers for W3 context and reasoning."""

from .schemas import ReasoningRequest, ReasoningResult


def validate_request(request: ReasoningRequest) -> ReasoningRequest:
    """Validate a reasoning request and return it."""
    if not request.question.strip():
        raise ValueError("Request question must not be empty.")

    if request.context.capture_enabled is not False:
        raise ValueError("Real screen capture must remain disabled.")

    return request


def validate_result(
    request: ReasoningRequest,
    result: ReasoningResult,
) -> ReasoningResult:
    """Ensure a result matches its request and references valid context items."""
    if result.request_id != request.request_id:
        raise ValueError("Result request_id does not match the request.")

    if result.prompt_version != request.prompt_version:
        raise ValueError("Result prompt_version does not match the request.")

    available_ids = {item.item_id for item in request.context.items}
    unknown_ids = set(result.grounded_item_ids) - available_ids

    if unknown_ids:
        raise ValueError(
            f"Result references unknown context item IDs: {sorted(unknown_ids)}"
        )

    if result.mode != "mock":
        raise ValueError("W3 reasoning must use mock mode.")

    return result
