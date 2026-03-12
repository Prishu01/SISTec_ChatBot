"""
Voice processing module for SISTec RAG Chatbot.

Handles speech recognition and text-to-speech conversion.
"""

import logging
import os
import platform
from pathlib import Path
from typing import Optional

import speech_recognition as sr
from gtts import gTTS

from config import VOICE_DURATION, VOICE_LANGUAGE, AUDIO_FILE
from utils import setup_logger, validate_duration, sanitize_text

logger = setup_logger(__name__)


class VoiceProcessor:
    """
    Handle voice input and output operations.
    
    Supports speech recognition (voice-to-text) and text-to-speech synthesis.
    """
    
    def __init__(self, enable_voice: bool = True):
        """
        Initialize voice processor.
        
        Args:
            enable_voice: Whether to enable voice features
        """
        self.enable_voice = enable_voice
        self.recognizer = sr.Recognizer()
        self.platform = platform.system()
        
        # Adjust recognizer settings for better accuracy
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        logger.info(f"VoiceProcessor initialized on {self.platform}")
    
    def record_voice(self, duration: int = VOICE_DURATION) -> str:
        """
        Record audio from microphone and convert to text.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recognized text, or empty string if recognition failed
        """
        if not self.enable_voice:
            logger.warning("Voice features disabled")
            return ""
        
        if not validate_duration(duration):
            logger.error(f"Invalid duration: {duration}")
            return ""
        
        try:
            logger.info(f"Starting voice recording for {duration} seconds...")
            print(f"🎙️ Listening ({duration}s)...")
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=duration + 2,
                    phrase_time_limit=duration
                )
            
            logger.info("Audio captured, recognizing...")
            
            # Try multiple recognition engines for robustness
            text = self._recognize_with_fallback(audio)
            
            if text:
                logger.info(f"Recognized: {text}")
                return text
            else:
                logger.warning("No speech recognized")
                return ""
                
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            print(f"❌ Speech service error: {e}")
            return ""
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            print("❌ Could not understand audio")
            return ""
            
        except Exception as e:
            logger.error(f"Unexpected error during voice recording: {e}")
            print(f"❌ Error: {e}")
            return ""
    
    def _recognize_with_fallback(self, audio: sr.AudioData) -> str:
        """
        Try multiple recognition engines as fallback.
        
        Args:
            audio: AudioData object from microphone
            
        Returns:
            Recognized text or empty string
        """
        try:
            # Primary: Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=VOICE_LANGUAGE)
            return text
            
        except sr.UnknownValueError:
            logger.debug("Google recognition failed, could not understand audio")
            return ""
            
        except sr.RequestError:
            logger.debug("Google recognition unavailable")
            return ""
    
    def text_to_speech(self, text: str, output_file: str = AUDIO_FILE) -> bool:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_voice:
            logger.warning("Voice features disabled")
            return False
        
        if not text or not isinstance(text, str):
            logger.error("Invalid text for TTS")
            return False
        
        try:
            # Sanitize text
            text = sanitize_text(text, max_length=5000)
            
            logger.info(f"Converting text to speech ({len(text)} chars)...")
            
            # Generate speech
            tts = gTTS(
                text=text,
                lang=VOICE_LANGUAGE,
                slow=False,
                lang_check=False
            )
            
            # Save file
            tts.save(output_file)
            logger.info(f"Audio saved to {output_file}")
            
            # Play audio based on platform
            self._play_audio(output_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during text-to-speech conversion: {e}")
            print(f"❌ TTS Error: {e}")
            return False
    
    def _play_audio(self, filepath: str) -> None:
        """
        Play audio file using platform-specific command.
        
        Args:
            filepath: Path to audio file
        """
        try:
            filepath = str(Path(filepath).absolute())
            
            if self.platform == "Windows":
                os.startfile(filepath)
                logger.info(f"Playing audio on Windows: {filepath}")
                
            elif self.platform == "Darwin":  # macOS
                os.system(f"afplay '{filepath}'")
                logger.info(f"Playing audio on macOS: {filepath}")
                
            elif self.platform == "Linux":
                os.system(f"aplay '{filepath}' 2>/dev/null || paplay '{filepath}'")
                logger.info(f"Playing audio on Linux: {filepath}")
                
            else:
                logger.warning(f"Audio playback not supported on {self.platform}")
                
        except Exception as e:
            logger.error(f"Error playing audio: {e}")


def get_voice_processor(enable_voice: bool = True) -> VoiceProcessor:
    """
    Factory function to get or create voice processor.
    
    Args:
        enable_voice: Whether to enable voice features
        
    Returns:
        VoiceProcessor instance
    """
    return VoiceProcessor(enable_voice=enable_voice)
