import os
import json
import logging
from vosk import Model, KaldiRecognizer
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for handling speech-to-text transcription using Vosk"""
    
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            logger.error(f"Vosk model not found at {model_path}")
            raise FileNotFoundError(
                f"Vosk model not found at {model_path}. "
                "Please download a model from https://alphacephei.com/vosk/models"
            )
        
        logger.info(f"Loading Vosk model from {model_path}")
        self.model = Model(model_path)
        self.sample_rate = 16000
        logger.info("Vosk model loaded successfully")
    
    def create_recognizer(self) -> KaldiRecognizer:
        """Create a new recognizer instance for a transcription session"""
        logger.debug("Creating new Kaldi recognizer")
        return KaldiRecognizer(self.model, self.sample_rate)
    
    def process_audio_chunk(
        self, 
        recognizer: KaldiRecognizer, 
        audio_data: bytes
    ) -> Dict[str, str]:
        """
        Process audio chunk and return partial or final result
        
        Args:
            recognizer: Vosk recognizer instance
            audio_data: Raw audio bytes
            
        Returns:
            Dict with 'type' ("partial" or "final") and 'text'
        """
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())
            return {
                "type": "final",
                "text": result.get("text", "").strip()
            }
        else:
            partial = json.loads(recognizer.PartialResult())
            return {
                "type": "partial",
                "text": partial.get("partial", "").strip()
            }
    
    def get_final_result(self, recognizer: KaldiRecognizer) -> str:
        """
        Get final transcription result when session ends
        
        Args:
            recognizer: Vosk recognizer instance
            
        Returns:
            Final transcription text
        """
        result = json.loads(recognizer.FinalResult())
        return result.get("text", "").strip()
    
# Example usage:
from app.services.read_audio import read_audio_as_bytes
if __name__ == "__main__":
    audio_path = r"C:\Users\Softvence\Documents\New folder\Transcription-app\backend\sample_audio.mp3"
    print("length of audio bytes:", len(read_audio_as_bytes(audio_path)))

    transcription_service = TranscriptionService(
        model_path="./models/vosk-model-small-en-us-0.15"
    )
    
    recognizer = transcription_service.create_recognizer()

    # Convert audio → bytes
    audio_bytes = read_audio_as_bytes(audio_path)

    # You can chunk the audio bytes in small parts too
    chunk_size = 4000
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i+chunk_size]
        result = transcription_service.process_audio_chunk(recognizer, chunk)

        if result["type"] == "final":
            print("Final:", result["text"])
        else:
            print("Partial:", result["text"])

    final_text = transcription_service.get_final_result(recognizer)
    print("Final Transcription:", final_text)


