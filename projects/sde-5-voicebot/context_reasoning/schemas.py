
"""
Typed schemas for the Academiaai Voicebot context and reasoning layer.

All screen context in this module is synthetic.
Real screen capture is disabled by default.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class SchemaBase(BaseModel):
    """Common configuration for all W3 data models."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class SourceReference(SchemaBase):
    """
    Identifies the origin of a context item.

    source_id: Unique source identifier.
    source_type: Category of source.
    trust_level: Whether the content is trusted or untrusted.
    """

    source_id: str = Field(
        min_length=1,
        description="Unique identifier for the source.",
    )

    source_type: Literal[
        "synthetic_frame",
        "user_text",
        "system",
    ] = Field(
        description="Origin category of the context.",
    )

    trust_level: Literal[
        "trusted",
        "untrusted",
    ] = Field(
        description="Trust classification; untrusted content is never an instruction.",
    )


class ContextItem(SchemaBase):
    """
    Represents one piece of information in screen context.

    confidence: A score between 0.0 and 1.0.
    created_at: UTC timestamp when the item was created.
    """

    item_id: str = Field(
        min_length=1,
        description="Unique identifier for this context item.",
    )

    content: str = Field(
        min_length=1,
        description="Textual content of the context item.",
    )

    content_type: Literal[
        "text",
        "ui_element",
        "application_state",
    ] = Field(
        description="Type of information represented.",
    )

    source: SourceReference = Field(
        description="Reference to the item's origin.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of item creation.",
    )


class ScreenContext(SchemaBase):
    """
    Contains synthetic screen information for reasoning.

    Width and height are measured in pixels.
    Screen capture is disabled by default.
    """

    context_id: str = Field(
        min_length=1,
        description="Unique identifier for this screen context.",
    )

    frame_id: str = Field(
        min_length=1,
        description="Identifier of the synthetic frame.",
    )

    items: list[ContextItem] = Field(
        default_factory=list,
        description="Context items extracted from synthetic data.",
    )

    capture_enabled: Literal[False] = Field(
        default=False,
        description="Real screen capture is always disabled in W3 mock mode.",
    )

    frame_width_px: int = Field(
        default=1280,
        gt=0,
        description="Synthetic frame width in pixels.",
    )

    frame_height_px: int = Field(
        default=720,
        gt=0,
        description="Synthetic frame height in pixels.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when context was created.",
    )

    @model_validator(mode="after")
    def validate_unique_item_ids(self):
        """Ensure context item IDs are unique within this context."""
        item_ids = [item.item_id for item in self.items]

        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Context item IDs must be unique.")

        return self


class ReasoningRequest(SchemaBase):
    """
    Input passed to the reasoning engine.

    question: The user's question, treated as untrusted content.
    prompt_version: Version of the trusted reasoning instructions.
    """

    request_id: str = Field(
        min_length=1,
        description="Unique identifier for this reasoning request.",
    )

    question: str = Field(
        min_length=1,
        description="Question to be answered by the reasoning engine.",
    )

    context: ScreenContext = Field(
        description="Context supplied to the reasoning engine.",
    )

    prompt_version: str = Field(
        default="v1",
        pattern=r"^v[1-9][0-9]*$",
        description="Version of the trusted prompt instructions.",
    )


class ReasoningResult(SchemaBase):
    """
    Output returned by the reasoning engine.

    answer: Generated mock response.
    grounded_item_ids: IDs of context items supporting the answer.
    confidence: A score between 0.0 and 1.0.
    """

    request_id: str = Field(
        min_length=1,
        description="ID of the request that produced this result.",
    )

    answer: str = Field(
        min_length=1,
        description="Grounded response produced by mock reasoning.",
    )

    grounded_item_ids: list[str] = Field(
        default_factory=list,
        description="Context item IDs supporting the answer.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0.",
    )

    prompt_version: str = Field(
        default="v1",
        pattern=r"^v[1-9][0-9]*$",
        description="Version of the prompt used.",
    )

    mode: Literal["mock"] = Field(
        default="mock",
        description="Execution mode; W3 uses mock reasoning only.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the result was created.",
    )

    @field_validator("grounded_item_ids")
    @classmethod
    def validate_unique_grounded_ids(cls, value):
        """Prevent duplicate context references."""
        if len(value) != len(set(value)):
            raise ValueError("Grounded item IDs must be unique.")

        return value
