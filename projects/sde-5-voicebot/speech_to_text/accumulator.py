from speech_to_text.schemas import TranscriptEvent


class TranscriptAccumulator:

    def __init__(self):
        self.segments = {}
        self.processed_event_ids = set()

    def add_event(self, event: TranscriptEvent):

        # Ignore duplicate events
        if event.event_id in self.processed_event_ids:
            return False

        self.processed_event_ids.add(event.event_id)

        # Ignore error events for transcript accumulation
        if event.event_type == "error":
            return False

        segment = event.segment
        chunk_id = segment.chunk_id

        existing = self.segments.get(chunk_id)

        # Add a new segment
        if existing is None:
            self.segments[chunk_id] = segment
            return True

        # Never replace a final segment with an interim segment
        if existing.is_final and not segment.is_final:
            return False

        # Replace an interim segment with a newer interim or final
        if not existing.is_final:
            self.segments[chunk_id] = segment
            return True

        return False

    def get_segments(self):

        return sorted(
            self.segments.values(),
            key=lambda segment: (
                segment.sequence_number,
                segment.start_ms
            )
        )

    def get_transcript(self):

        return " ".join(
            segment.text for segment in self.get_segments()
        )