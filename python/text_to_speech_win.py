import json
import sys
import win32com.client
import threading
import time
import winsound  # Added for beep functionality
import subprocess
import os
import argparse
import pythoncom
import requests  # For ElevenLabs API
import io
import tempfile
# import elevenlabs 

# Remove pydub dependency
PYDUB_AVAILABLE = False

class TextToSpeech:
    def __init__(self, use_google_cloud=False, google_cloud_credentials=None):
        # Google Cloud configuration
        self.use_google_cloud = use_google_cloud
        self.google_cloud_credentials = google_cloud_credentials
        
        if self.use_google_cloud:
            # Initialize Google Cloud Text-to-Speech client
            self.client = texttospeech.TextToSpeechClient.from_service_account_json(self.google_cloud_credentials)
        
        try:
            # Initialize the SAPI voice directly using win32com
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Try to select a more natural-sounding voice if available
            voices = self.speaker.GetVoices()
            for i in range(voices.Count):
                voice = voices.Item(i)
                # Prefer Microsoft Ryan (Natural) voice if available
                if "Ryan" in voice.GetDescription() and "Natural" in voice.GetDescription():
                    self.speaker.Voice = voice
                    print(f"Using voice: {voice.GetDescription()}")
                    break
                # Fall back to Zira or David if Ryan not available
                elif "Zira" in voice.GetDescription() or "David" in voice.GetDescription():
                    self.speaker.Voice = voice
                    print(f"Using voice: {voice.GetDescription()}")
                    break
            
            # Set a slightly slower rate for more natural speech
            self.speaker.Rate = 1  # Range is -10 to 10, with 0 being default
            
            # Flag to control speech interruption
            self.speaking = False
        except Exception as e:
            print(f"Error initializing text-to-speech: {str(e)}")
            self.speaker = None
    
    def speak_google_cloud(self, text):
        """Use Google Cloud Text-to-Speech API to generate and play speech"""
        if not self.client:
            print("Google Cloud Text-to-Speech client not initialized.")
            return self.speak_windows(text)
            
        try:
            self.speaking = True
            print(f"Speaking with Google Cloud: {text[:50]}..." if len(text) > 50 else f"Speaking with Google Cloud: {text}")
            
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            # Save to temporary file and play with Windows Media Player
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.audio_content)
                temp_file_path = temp_file.name
            
            # Play using default media player
            os.startfile(temp_file_path)
            
            # Wait for audio to finish (approximate)
            estimated_duration = len(text) / 15
            time.sleep(estimated_duration)
            
            # Try to delete the temp file after playing
            try:
                os.unlink(temp_file_path)
            except:
                pass  # File might be locked by media player
            
            self.speaking = False
            return True
        except Exception as e:
            print(f"Error in Google Cloud text-to-speech: {str(e)}")
            self.speaking = False
            return self.speak_windows(text)
    
    def speak_windows(self, text):
        """Use Windows TTS to speak text"""
        if self.speaker:
            # Set speaking flag
            self.speaking = True
            
            # Fix common pronunciation issues
            pronunciation_fixes = {
                "AI": "A.I.",
                "API": "A.P.I.",
                "SQL": "sequel",
                "GUI": "gooey",
                # Add more word fixes as needed
            }
            
            for word, pronunciation in pronunciation_fixes.items():
                text = text.replace(f" {word} ", f" <phoneme alphabet=\"ipa\" ph=\"{pronunciation}\"> {word} </phoneme> ")
            
            # Speak the text
            print(f"Speaking with Windows TTS: {text[:50]}..." if len(text) > 50 else f"Speaking with Windows TTS: {text}")
            self.speaker.Speak(text)
            
            # Reset speaking flag
            self.speaking = False
            return True
        else:
            print("Text-to-speech engine not available")
            return False
    
    def speak(self, text, humanize=False):
        try:
            # Use Google Cloud if enabled
            if self.use_google_cloud:
                return self.speak_google_cloud(text)
            else:
                return self.speak_windows(text)
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")
            self.speaking = False
            return False

    @staticmethod
    def download_voice():
        """Attempt to download additional voices using PowerShell"""
        print("Attempting to download additional voices...")
        try:
            # PowerShell command to open the Speech settings
            ps_command = """
            # Open Settings to Speech page
            Start-Process "ms-settings:speech"
            
            Write-Host "Settings app opened to Speech page."
            Write-Host "Please:"
            Write-Host "1. Click on 'Add voices'"
            Write-Host "2. Select the voices you want to install"
            Write-Host "3. Click 'Add' to download and install the voices"
            """
            
            # Execute PowerShell command
            subprocess.run(["powershell", "-Command", ps_command], 
                          capture_output=True, text=True)
            
            print("Please follow the instructions in the Settings app to download voices.")
            print("After installing voices, restart your application to use them.")
            return True
        except Exception as e:
            print(f"Error launching voice download: {str(e)}")
            print("You can manually download voices by going to:")
            print("Settings > Time & Language > Speech > Add voices")
            return False
    
    def stop_speaking(self):
        """Stop the current speech"""
        if self.speaker and self.speaking:
            self.speaker.Speak("", 3)  # 3 is SVSFPurgeBeforeSpeak | SVSFIsXML
            self.speaking = False
            print("Speech stopped.")
    
    def play_beep(self):
        """Play a beep sound to indicate listening has started"""
        # Frequency of 800 Hz, duration of 300 milliseconds
        winsound.Beep(800, 300)
    
    def set_speech_rate(self, rate):
        """Adjust the speech rate
        
        Args:
            rate: Integer from -10 (very slow) to 10 (very fast)
        """
        if self.speaker:
            if rate < -10:
                rate = -10
            elif rate > 10:
                rate = 10
            
            self.speaker.Rate = rate
            return True
        return False

    def set_volume(self, volume):
        """Adjust the speech volume
        
        Args:
            volume: Integer from 0 (silent) to 100 (loudest)
        """
        if self.speaker:
            if volume < 0:
                volume = 0
            elif volume > 100:
                volume = 100
            
            self.speaker.Volume = volume
            return True
        return False
    
    def emphasize_text(self, text):
        """Add emphasis to important words in the text
        
        Args:
            text: The text to be spoken
        Returns:
            Text with SSML emphasis tags
        """
        # Words to emphasize
        emphasis_words = ["important", "critical", "urgent", "warning", "danger", "remember"]
        
        for word in emphasis_words:
            text = text.replace(f" {word} ", f" <emphasis level='strong'>{word}</emphasis> ")
        
        return text
    
    def speak_with_emotion(self, text, emotion="neutral"):
        """Speak text with a specific emotion
        
        Args:
            text: The text to be spoken
            emotion: One of "happy", "sad", "angry", "neutral"
        """
        if not self.speaker:
            return False
            
        # Adjust rate and pitch based on emotion
        original_rate = self.speaker.Rate
        
        if emotion == "happy":
            self.speaker.Rate = original_rate + 1
            emotion_text = f"<prosody pitch='+15%' range='80%'>{text}</prosody>"
        elif emotion == "sad":
            self.speaker.Rate = original_rate - 2
            emotion_text = f"<prosody pitch='-10%' range='40%'>{text}</prosody>"
        elif emotion == "angry":
            self.speaker.Rate = original_rate + 2
            emotion_text = f"<prosody pitch='+5%' range='90%' volume='loud'>{text}</prosody>"
        else:  # neutral
            emotion_text = text
            
        # Speak with emotion
        result = self.speak(emotion_text)
        
        # Reset rate
        self.speaker.Rate = original_rate
        
        return result

# Add this at the end of the file
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Text-to-Speech Service')
    parser.add_argument('--background', action='store_true', help='Run in background mode')
    parser.add_argument('--text', type=str, help='Text to speak')
    args = parser.parse_args()
    
    # If running in background mode
    if args.background:
        print("Starting TTS service in background mode...")
        print("Logs will appear in this window")
        print("Press Ctrl+C to exit")
        
        # Initialize COM in this thread
        pythoncom.CoInitialize()
        
        # Create TTS instance
        tts = TextToSpeech()
        
        try:
            while True:
                # Check for input from stdin (can be extended to read from a file or socket)
                if sys.stdin.isatty():  # Only try to read if stdin is a terminal
                    try:
                        line = input("Enter text to speak (or 'exit' to quit): ")
                        if line.lower() == 'exit':
                            break
                        tts.speak(line)
                    except EOFError:
                        # No input available
                        time.sleep(1)
                else:
                    # If not connected to a terminal, just wait
                    time.sleep(1)
        except KeyboardInterrupt:
            print("Service stopped by user")
        finally:
            pythoncom.CoUninitialize()
    else:
        # Original behavior for direct calls or from Node.js
        if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
            text = sys.argv[1]
        elif args.text:
            text = args.text
        else:
            # Read from stdin if no arguments
            data = sys.stdin.read()
            try:
                input_data = json.loads(data)
                text = input_data.get("text", "")
            except:
                text = data
        
        tts = TextToSpeech()
        result = tts.speak(text)
        print(json.dumps({"success": result}))