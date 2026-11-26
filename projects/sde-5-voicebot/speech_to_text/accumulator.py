from speech_to_text.schemas import TranscriptEvent


class TranscriptAccumulator:
    """
    Maintains session-aware transcript segments.

    Supports:
    - Interim transcript events
    - Transcript revisions
    - Finalization events
    - Duplicate event prevention
    - Out-of-order event protection
    - Multiple independent sessions
    """

    def __init__(self):
        self.segments = {}
        self.processed_event_ids = set()
        self.last_event_timestamps = {}

    def add_event(self, event: TranscriptEvent):
        """
        Add a transcript event to the accumulator.

        Returns:
            True: Event successfully added or updated.
            False: Duplicate, error or outdated event.
        """

        # Identify events independently within each session.
        event_key = (event.session_id, event.event_id)

        # Ignore duplicate events.
        if event_key in self.processed_event_ids:
            return False

        self.processed_event_ids.add(event_key)

        # Error events are not transcript segments.
        if event.event_type == "error":
            return False

        segment = event.segment

        # Identify each segment using session and chunk.
        segment_key = (
            event.session_id,
            segment.chunk_id
        )

        existing = self.segments.get(segment_key)

        # Prevent older events from overwriting newer revisions.
        previous_timestamp = self.last_event_timestamps.get(
            segment_key
        )

        if (
            previous_timestamp is not None
            and event.timestamp_ms < previous_timestamp
        ):
            return False

        # Add a new segment.
        if existing is None:
            self.segments[segment_key] = segment
            self.last_event_timestamps[segment_key] = (
                event.timestamp_ms
            )
            return True

        # Never overwrite an already finalized segment.
        if existing.is_final:
            return False

        # Update an interim segment with a newer revision
        # or final transcript.
        self.segments[segment_key] = segment

        self.last_event_timestamps[segment_key] = (
            event.timestamp_ms
        )

        return True

    def get_segments(self, session_id=None):
        """
        Return transcript segments in sequence order.

        If session_id is supplied, return only that session.
        Otherwise, return segments from all sessions.
        """

        segments = [
            segment
            for (stored_session_id, _), segment
            in self.segments.items()
            if (
                session_id is None
                or stored_session_id == session_id
            )
        ]

        return sorted(
            segments,
            key=lambda segment: (
                segment.session_id,
                segment.sequence_number,
                segment.start_ms
            )
        )

    def get_transcript(self, session_id=None):
        """
        Return the combined transcript.

        Optionally filter by session ID.
        """

        return " ".join(
            segment.text
            for segment in self.get_segments(session_id)
        )