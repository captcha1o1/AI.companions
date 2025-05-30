"""Voice handling functionality for the anime AI."""

import os
import tempfile
import pyaudio
import wave
from faster_whisper import WhisperModel
import edge_tts
from pygame import mixer
import asyncio
from ..utils.text_processor import TextProcessor

class VoiceRecorder:
    def __init__(self):
        self.is_recording = False
        self.whisper_model = None
        try:
            self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        except Exception as e:
            print(f"Warning: Could not load Whisper model: {e}")
            self.whisper_model = None

    def record_audio(self, duration=5, sample_rate=16000):
        """Record audio from microphone"""
        try:
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            
            audio = pyaudio.PyAudio()
            stream = audio.open(format=format,
                              channels=channels,
                              rate=sample_rate,
                              input=True,
                              frames_per_buffer=chunk)
            
            frames = []
            for _ in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                wave_file = wave.open(tmp_file.name, 'wb')
                wave_file.setnchannels(channels)
                wave_file.setsampwidth(audio.get_sample_size(format))
                wave_file.setframerate(sample_rate)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()
                return tmp_file.name
                
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def transcribe_audio(self, audio_file):
        """Transcribe audio using faster-whisper"""
        if not self.whisper_model or not audio_file:
            return None
            
        try:
            segments, info = self.whisper_model.transcribe(audio_file, beam_size=5)
            text = ""
            for segment in segments:
                text += segment.text
            return text.strip()
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

class TextToSpeech:
    @staticmethod
    async def text_to_speech(text, voice="en-US-JennyNeural", rate="-5%", pitch="+0Hz"):
        """Convert text to speech using edge-tts"""
        try:
            # Preprocess text before TTS
            processed_text = TextProcessor.preprocess_for_tts(text)
            
            communicate = edge_tts.Communicate(processed_text, voice, rate=rate, pitch=pitch)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_wav_path = tmp_file.name
            
            await communicate.save(tmp_wav_path)
            return tmp_wav_path
                
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

    @staticmethod
    async def play_audio(audio_file):
        """Play audio file using pygame mixer"""
        try:
            mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            mixer.init()
            
            sound = mixer.Sound(audio_file)
            sound.set_volume(0.7)
            channel = sound.play()
            
            while channel.get_busy():
                await asyncio.sleep(0.1)
                
            mixer.quit()
            
        except Exception as e:
            print(f"Audio playback failed: {e}")
            print("Try installing: pip install pygame --upgrade") 