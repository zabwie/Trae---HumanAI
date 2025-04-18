import json
import sys
import speech_recognition as sr

class SpeechToText:
    def __init__(self):
        """Initialize Google speech recognition with optimized settings"""
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise and sensitivity
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def start_listening(self, timeout=5, phrase_time_limit=10, tts=None):
        """
        Start listening for speech input using Google's speech recognition
        
        Args:
            timeout (int): Maximum time to wait for speech to start
            phrase_time_limit (int): Maximum time for a single phrase
            tts: Optional text-to-speech object for audio feedback
        """
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise... Please wait.")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Listening... Speak now.")
                # Play beep if text-to-speech object is provided
                if tts:
                    tts.play_beep()
                
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                print("Processing speech...")
                # Use Google's speech recognition
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period.")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            return ""

if __name__ == "__main__":
    # This will be used when called directly from Node.js
    stt = SpeechToText()
    result = stt.start_listening()
    print(json.dumps({"text": result}))