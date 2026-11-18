"""Provider-free LLM adapter with bounded retries and strict result checks."""

from typing import Protocol
import json
import math

from pydantic import ValidationError

from .mock_reasoning import run_mock_reasoning
from .schemas import ReasoningRequest, ReasoningResult
from .validation import validate_request, validate_result


class LLMAdapterError(RuntimeError):
    """Raised when a client fails or returns invalid structured output."""


class LLMClient(Protocol):
    """Interface for clients that return structured reasoning output.

    Implementations must honor ``timeout_seconds`` for their own I/O operation.
    """

    def generate(
        self,
        request: ReasoningRequest,
        timeout_seconds: float,
    ) -> str | dict[str, object]:
        """Return a JSON object or its JSON-encoded representation."""


class MockLLMClient:
    """Adapt the existing deterministic mock reasoning function to this interface."""

    def generate(
        self,
        request: ReasoningRequest,
        timeout_seconds: float,
    ) -> dict[str, object]:
        """Return a structured result without network access or credentials."""
        del timeout_seconds
        return run_mock_reasoning(request).model_dump(mode="json")


class LLMAdapter:
    """Call an LLM client and validate its output as a grounded mock result."""

    def __init__(
        self,
        client: LLMClient | None = None,
        timeout_seconds: float = 5.0,
        max_retries: int = 2,
    ) -> None:
        if (
            not isinstance(timeout_seconds, (int, float))
            or isinstance(timeout_seconds, bool)
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
            raise ValueError("Timeout must be a positive finite number.")
        if (
            not isinstance(max_retries, int)
            or isinstance(max_retries, bool)
            or max_retries < 0
        ):
            raise ValueError("Maximum retries must be a non-negative integer.")

        self.client = client or MockLLMClient()
        self.timeout_seconds = float(timeout_seconds)
        self.max_retries = max_retries

    def complete(self, request: ReasoningRequest) -> ReasoningResult:
        """Return a schema-validated result, retrying only transient failures."""
        validate_request(request)
        output: str | dict[str, object] | None = None

        for attempt in range(self.max_retries + 1):
            try:
                output = self.client.generate(
                    request,
                    timeout_seconds=self.timeout_seconds,
                )
                break
            except (TimeoutError, ConnectionError) as error:
                if attempt == self.max_retries:
                    raise LLMAdapterError(
                        "LLM client failed after the configured retries."
                    ) from error

        payload = self._parse_output(output)
        try:
            result = ReasoningResult.model_validate(payload)
            return validate_result(request, result)
        except (ValidationError, ValueError, TypeError) as error:
            raise LLMAdapterError("LLM client returned invalid or unsafe output.") from error

    @staticmethod
    def _parse_output(
        output: str | dict[str, object] | None,
    ) -> dict[str, object]:
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError as error:
                raise LLMAdapterError("LLM client returned malformed JSON.") from error

        if not isinstance(output, dict):
            raise LLMAdapterError("LLM client output must be a JSON object.")
        return output