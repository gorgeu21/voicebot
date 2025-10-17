"""
Audio transcription module using OpenAI Whisper API
Handles voice message transcription with speaker diarization support
"""
import io
import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, TRANSCRIPTION_MODEL, MAX_AUDIO_SIZE_MB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class AudioTranscriber:
    """Handles audio transcription using OpenAI Whisper API"""
    
    def __init__(self):
        self.max_file_size = MAX_AUDIO_SIZE_MB * 1024 * 1024  # Convert to bytes
        
    async def transcribe_audio(self, file_bytes: bytes, filename: str = "audio.ogg") -> Dict[str, Any]:
        """
        Transcribe audio file to text with speaker detection
        
        Args:
            file_bytes: Audio file content as bytes
            filename: Original filename for proper format detection
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Validate file size
            if len(file_bytes) > self.max_file_size:
                raise ValueError(f"Audio file too large: {len(file_bytes)} bytes. Max allowed: {self.max_file_size} bytes")
            
            logger.info(f"Starting transcription for {filename} ({len(file_bytes)} bytes)")
            
            # Create file-like object for OpenAI API
            audio_file = io.BytesIO(file_bytes)
            audio_file.name = filename
            
            # Call OpenAI Whisper API
            response = await client.audio.transcriptions.create(
                file=audio_file,
                model=TRANSCRIPTION_MODEL,
                response_format="verbose_json",
                language="ru",  # Russian language
                prompt="Это голосовое сообщение на русском языке. Пожалуйста, транскрибируйте с указанием говорящих, если их несколько."
            )
            
            # Extract transcription data
            transcription_text = response.text
            segments = getattr(response, 'segments', [])
            
            logger.info(f"Transcription completed successfully. Text length: {len(transcription_text)} characters")
            
            # Process segments to identify speakers (basic approach)
            processed_text = self._process_segments_with_speakers(transcription_text, segments)
            
            return {
                "success": True,
                "text": transcription_text,
                "processed_text": processed_text,
                "segments": segments,
                "language": getattr(response, 'language', 'ru'),
                "duration": getattr(response, 'duration', 0)
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "processed_text": ""
            }
    
    def _process_segments_with_speakers(self, full_text: str, segments: list) -> str:
        """
        Process transcription segments to add basic speaker identification
        
        Args:
            full_text: Complete transcription text
            segments: List of transcription segments with timestamps
            
        Returns:
            Formatted text with speaker markers
        """
        if not segments:
            return f"**Говорящий:** {full_text}"
        
        # Simple speaker detection based on pauses and voice characteristics
        # This is a basic implementation - for better results, use specialized diarization services
        processed_segments = []
        current_speaker = 1
        last_end_time = 0
        
        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            # Detect speaker change based on pause duration (simple heuristic)
            pause_duration = start_time - last_end_time
            if pause_duration > 2.0 and i > 0:  # 2 second pause might indicate speaker change
                current_speaker += 1
            
            # Format timestamp
            start_min = int(start_time // 60)
            start_sec = int(start_time % 60)
            timestamp = f"{start_min:02d}:{start_sec:02d}"
            
            processed_segments.append(f"**Говорящий {current_speaker}** [{timestamp}]: {text}")
            last_end_time = end_time
        
        if processed_segments:
            return "\n\n".join(processed_segments)
        else:
            return f"**Говорящий:** {full_text}"
    
    def get_audio_info(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Get basic information about audio file
        
        Args:
            file_bytes: Audio file content as bytes
            
        Returns:
            Dictionary with audio file information
        """
        return {
            "size_bytes": len(file_bytes),
            "size_mb": round(len(file_bytes) / (1024 * 1024), 2),
            "within_limits": len(file_bytes) <= self.max_file_size
        }

# Global transcriber instance
transcriber = AudioTranscriber()

async def transcribe_voice_message(file_bytes: bytes, filename: str = "voice.ogg") -> Dict[str, Any]:
    """
    Convenience function for transcribing voice messages
    
    Args:
        file_bytes: Audio file content as bytes
        filename: Original filename
        
    Returns:
        Transcription results
    """
    return await transcriber.transcribe_audio(file_bytes, filename)
