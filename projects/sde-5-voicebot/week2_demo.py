"""Demonstrate the synthetic-only Week 2 context and reasoning adapters."""

from context_reasoning.capture_adapter import (
    CaptureConfig,
    MockVisionAdapter,
    OptInCaptureAdapter,
)
from context_reasoning.context_builder import ContextBuildConfig, ContextBuilder
from context_reasoning.llm_adapter import LLMAdapter
from context_reasoning.schemas import ReasoningRequest


def main() -> None:
    capture = OptInCaptureAdapter(
        MockVisionAdapter("Synthetic screen shows a Submit button"),
        CaptureConfig(enabled=True, sample_interval_seconds=1.0),
    )
    capture.opt_in()

    context = capture.process_frame(
        frame_data=b"synthetic-frame-fixture",
        frame_id="demo-frame-001",
        timestamp=0.0,
    )
    if context is None:
        raise RuntimeError("The first synthetic frame should be sampled.")

    bounded_context = ContextBuilder(
        ContextBuildConfig(max_tokens=200, max_age_seconds=300),
    ).build(context, question="What button is shown?")

    request = ReasoningRequest(
        request_id="week2-demo-001",
        question="What button is shown?",
        context=bounded_context,
    )
    result = LLMAdapter().complete(request)

    print("WEEK 2 SYNTHETIC CONTEXT DEMO")
    print(f"Capture enabled in ScreenContext: {bounded_context.capture_enabled}")
    print(f"Context items: {len(bounded_context.items)}")
    print(f"Mock answer: {result.answer}")
    print(f"Grounded item IDs: {result.grounded_item_ids}")


if __name__ == "__main__":
    main()