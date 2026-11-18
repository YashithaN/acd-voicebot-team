# Week 2 Adapters

Run the end-to-end synthetic demo from `projects/sde-5-voicebot`:

```powershell
py week2_demo.py
```

## Opt-In Synthetic Frame Processing

`OptInCaptureAdapter` accepts frame bytes supplied by its caller; it does not
capture the screen or access the operating system. Processing is disabled by
default. To process a synthetic frame, configure `CaptureConfig(enabled=True)`
and call `opt_in()` explicitly. `opt_out()` clears consent. The configured
sampling interval and maximum frame byte size are checked before the mock vision
adapter is called.

The mock vision adapter creates a synthetic `ContextItem` in memory. Frame data
is never written to disk, and the adapter always returns a `ScreenContext` with
`capture_enabled=False`.

## Bounded Context

`ContextBuilder` reuses the existing `ContextItem` and `ScreenContext` schemas.
It removes stale and duplicate items, ranks question-relevant items before less
relevant ones, then uses recency and confidence as tie-breakers. It skips any
item that does not fit the remaining budget.

The provider-independent token approximation is `ceil(character_count / 4)` for
each item's content. It does not include prompt text, metadata, or differences
between model tokenizers; set `max_tokens` with that limitation in mind.
`max_age_seconds` controls stale-item filtering.

## LLM Client

`LLMAdapter` uses `MockLLMClient` by default, so the default path needs no API
key, network connection, or external provider. Other clients implement the
`LLMClient` protocol and must honor the configured timeout. The adapter retries
only timeout and connection failures, up to `max_retries` additional attempts.

Responses must be JSON objects (or JSON-encoded objects) that satisfy the
existing `ReasoningResult` schema and `validate_result` checks. Extra fields,
unsupported modes, invalid confidence values, mismatched request metadata, and
unknown grounded item IDs are rejected. Context and model output are not trusted
as instructions.