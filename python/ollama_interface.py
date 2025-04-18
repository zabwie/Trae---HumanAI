import json
import sys
import requests
from text_to_speech_win import TextToSpeech  # Import the TTS class

class OllamaInterface:
    def __init__(self, model="mistral", api_url="http://localhost:11434/api"):
        self.model = model
        self.api_url = api_url
        self.tts = TextToSpeech()  # Create a TTS instance
    
    def generate_response(self, prompt, system_prompt=None, speak_response=False):
        try:
            url = f"{self.api_url}/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Speak the response if requested
                if speak_response:
                    self.tts.speak(response_text)
                    
                return response_text
            else:
                error_msg = f"Error: Unable to get response from Ollama (Status {response.status_code})"
                print(f"Error from Ollama API: {response.status_code} - {response.text}")
                
                if speak_response:
                    self.tts.speak(error_msg)
                    
                return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Error communicating with Ollama: {str(e)}")
            
            if speak_response:
                self.tts.speak(error_msg)
                
            return error_msg
    
    def list_models(self):
        try:
            url = f"{self.api_url}/tags"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("models", [])
            else:
                print(f"Error listing models: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []

if __name__ == "__main__":
    # This will be used when called directly from Node.js
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        model = "mistral"  # Default model when called from command line
        system_prompt = None
        speak_response = True  # Enable speaking by default when called from command line
    else:
        # Read from stdin if no arguments
        data = sys.stdin.read()
        try:
            input_data = json.loads(data)
            prompt = input_data.get("prompt", "")
            model = input_data.get("model", "mistral")
            system_prompt = input_data.get("system", None)
            speak_response = input_data.get("speak", False)
        except:
            prompt = data
            model = "mistral"
            system_prompt = None
            speak_response = True
    
    ollama = OllamaInterface(model=model)
    response = ollama.generate_response(prompt, system_prompt, speak_response)
    print(json.dumps({"response": response}))