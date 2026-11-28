from abc import ABC, abstractmethod
from typing import List

from speech_to_text.schemas import TranscriptEvent


class SpeechToTextAdapter(ABC):
    """
    Common interface for speech-to-text providers.
    """

    @abstractmethod
    def transcribe(self, audio_chunk: dict) -> List[TranscriptEvent]:
        """
        Convert an audio chunk into transcript events.
        """
        pass