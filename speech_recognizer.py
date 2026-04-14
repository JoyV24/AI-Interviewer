import streamlit as st
import speech_recognition as sr
from typing import Optional

class SpeechRecognizer:
    """Utility class that records audio from the default microphone
    and transcribes it to text using Google's free Speech‑to‑Text API.

    If you need a paid / more accurate backend you can swap the recognizer
    call (e.g., to Azure, AWS Transcribe, or OpenAI Whisper) inside
    ``_recognize``.
    """

    def __init__(self):
        # Create a recognizer instance once; reuse it for better performance.
        self.recognizer = sr.Recognizer()
        # Reduce noise influence.
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def record(self, timeout: int = 10, phrase_time_limit: Optional[int] = None) -> Optional[str]:
        """Record from mic and immediately transcribe.

        :param timeout: Seconds to wait for user to start speaking.
        :param phrase_time_limit: Seconds after which to stop recording automatically.
        :return: The transcribed text or ``None`` if transcription failed.
        """
        try:
            with sr.Microphone() as source:
                st.info("🎤 Listening… please speak now.")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            st.warning("⌚ Timeout – no speech detected.")
            return None

        return self._recognize(audio)

    def transcribe_file(self, wav_path: str) -> Optional[str]:
        """Transcribe an existing WAV/FLAC audio file."""
        try:
            with sr.AudioFile(wav_path) as source:
                audio = self.recognizer.record(source)
        except Exception as e:
            st.error(f"Failed to load audio file: {e}")
            return None

        return self._recognize(audio)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _recognize(self, audio: sr.AudioData) -> Optional[str]:
        """Send *audio* to Google Speech‑to‑Text and handle errors."""
        try:
            text = self.recognizer.recognize_google(audio)
            if text:
                st.success("✅ Speech transcribed successfully!")
            return text
        except sr.UnknownValueError:
            st.warning("🤔 Couldn’t understand the speech.")
        except sr.RequestError as e:
            st.error(f"🚨 Couldn’t request results from Google STT service: {e}")
        return None
