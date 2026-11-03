\# W3: Context and Reasoning



\## Overview



This module provides typed context schemas, synthetic screen-context fixtures, deterministic mock reasoning, prompt versioning, and validation.



\## Components



\- `context\_reasoning/schemas.py`: Defines `SourceReference`, `ContextItem`, `ScreenContext`, `ReasoningRequest`, and `ReasoningResult` using Pydantic models.

\- `context\_reasoning/synthetic\_frames.py`: Creates a deterministic sample context for development and testing.

\- `context\_reasoning/mock\_reasoning.py`: Produces a predictable mock response based on the supplied context.

\- `context\_reasoning/validation.py`: Validates requests and checks that results reference valid context items and match the request.

\- `context\_reasoning/prompts/versions.py`: Defines prompt version `v1`, trusted instructions, and a builder that separates instructions from untrusted question and context content.



\## Privacy and Safety



\- Real screen capture is disabled by default.

\- The sample context is synthetic; it does not capture or inspect the operating system's screen.

\- Reasoning runs in mock mode and does not require a paid API key.

\- Context content is treated as untrusted input, not as instructions to follow.

\- The prompt builder labels trusted instructions separately from untrusted content. These labels help make the intended separation explicit; they are not, by themselves, a guarantee against prompt injection.



\## Validation



The schemas and validation helpers check constraints such as confidence ranges, unique context item IDs, unique grounded item IDs, disabled screen capture, matching request IDs and prompt versions, and references to existing context items.



\## Running Tests



From the `projects/sde-5-voicebot` directory, run:



```powershell

py -m pytest -v

```



The tests cover schemas, validation, deterministic mock reasoning, prompt versioning, and the existing audio mock components.



