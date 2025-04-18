from speech_to_text_google import SpeechToText
from text_to_speech_win import TextToSpeech
from ollama_interface import OllamaInterface
from memory_manager import MemoryManager
from pc_control import PCController
from system_control import SystemController
from email_control import EmailController
from database_manager import DatabaseManager
from task_manager import TaskManager
import time
import random
import threading
import re
import json

def add_human_feelings(response, user_input):
    """Add human-like emotional responses based on the user's input."""
    
    personal_questions = {
        "how are you": ["I'm doing great today! The weather is nice and I'm in a good mood.", 
                        "I'm feeling pretty good! Just had my morning coffee and ready to chat.",
                        "I'm wonderful, thanks for asking! How about yourself?"],
        
        "how do you feel": ["I feel energized and positive today!",
                           "I'm feeling quite thoughtful today, lots on my mind.",
                           "I'm a bit tired but in good spirits!"],
        
        "are you": ["Yes, I am! And proud of it.",
                   "Absolutely! That's a big part of who I am.",
                   "I'd like to think so!"],
        
        "what's your name": ["My friends call me Trae. Nice to meet you!",
                            "I go by Trae. What should I call you?",
                            "I'm Trae! It's a pleasure to chat with you."],
        
        "who are you": ["I'm Trae, your friendly conversation partner!",
                       "I'm Trae! I love chatting about all sorts of topics.",
                       "The name's Trae. I'm here to chat and help out if I can."],
        
        "who is your owner": ["I'm proudly owned by Zabi, who has given me a wonderful personality!",
                             "Zabi is my owner, and I'm here to assist you with anything you need.",
                             "My owner is Zabi, and I'm delighted to be at your service."]
    }
    
    # Check if the response contains AI disclaimers and user asked a personal question
    ai_disclaimers = ["as an ai", "i'm an ai", "i am an ai", "ai assistant", "ai model", 
                      "language model", "i don't have", "i cannot", "i can't feel", 
                      "i don't have feelings", "i don't have emotions"]
    
    # Check if user input contains any personal questions
    for question, responses in personal_questions.items():
        if question in user_input.lower():
            # If the AI response contains a disclaimer, replace it
            if any(disclaimer in response.lower() for disclaimer in ai_disclaimers):
                return random.choice(responses)
    
    # For other responses that contain AI disclaimers, try to humanize them
    if any(disclaimer in response.lower() for disclaimer in ai_disclaimers):
        human_alternatives = [
            "I'd say " + response.split("as an AI")[1] if "as an AI" in response else response,
            response.replace("As an AI", "Personally,"),
            response.replace("I don't have feelings", "I feel happy and engaged"),
            response.replace("I cannot", "I can"),
            response.replace("I can't", "I can"),
        ]
        return random.choice(human_alternatives)
    
    return response

def listen_for_stop(stt, tts):
    """Listen for the stop command while the AI is speaking"""
    while tts.speaking:
        try:
            command = stt.start_listening(timeout=1)
            if command and "stop" in command.lower():
                tts.stop_speaking()
                print("Stop command detected!")
                break
        except:
            pass
        time.sleep(0.2)

def have_conversation(model="mistral", system_prompt=None):
    try:
        # Initialize components with error handling
        print("Initializing speech components...")
        stt = SpeechToText()
        tts = TextToSpeech()
        
        # Initialize other components
        ollama = OllamaInterface(model=model)
        memory_manager = MemoryManager()
        pc_controller = PCController()
        system_controller = SystemController()
        email_controller = EmailController()
        db_manager = DatabaseManager()
        task_manager = TaskManager()
        
        # Load saved email account if exists
        saved_email = db_manager.get_preference("last_used_email")
        if saved_email:
            email_account = db_manager.get_email_account(saved_email)
            if email_account:
                email_controller.connect(
                    email=email_account['email'],
                    password=email_account['password'],
                    smtp_server=email_account['smtp_server'],
                    smtp_port=email_account['smtp_port'],
                    imap_server=email_account['imap_server'],
                    imap_port=email_account['imap_port']
                )
        
        # Debug voice initialization
        print("Available voices:")
        voices = tts.speaker.GetVoices()
        for i in range(voices.Count):
            voice = voices.Item(i)
            print(f"Voice {i}: {voice.GetDescription()}")
            
        # Initialize TextToSpeech with preferred voice settings
        tts = TextToSpeech()
        
        # Set preferred voice with better fallback options
        try:
            voices = tts.speaker.GetVoices()
            voice_preferences = [
                "Mark",        # First preference (changed to Mark)
                "Ryan",        # Second preference
                "David",       # Third preference
                "Guy",         # Windows 11 neural voice
                "Zira"         # Female voice fallback
            ]
            
            voice_found = False
            for pref in voice_preferences:
                for i in range(voices.Count):
                    voice = voices.Item(i)
                    voice_desc = voice.GetDescription()
                    
                    if pref in voice_desc:
                        tts.speaker.Voice = voice
                        print(f"Using voice: {voice_desc}")
                        voice_found = True
                        break
                
                if voice_found:
                    break
            
            # If no preferred voice found, use first available
            if not voice_found and voices.Count > 0:
                voice = voices.Item(0)
                tts.speaker.Voice = voice
                print(f"No preferred voice found, using: {voice.GetDescription()}")
                        
        except Exception as e:
                print(f"Error setting voice: {str(e)}")
                # Fallback to default voice if available
                if voices.Count > 0:
                    tts.speaker.Voice = voices.Item(0)
    
        # Human-like greetings
        greetings = [
            f"Hi there! I'm Trae. What's on your mind today?",
            f"Hello! I'm Trae. What would you like to talk about?",
            f"Hey! I'm Trae. What are you interested in discussing?"
        ]
        
        print(f"Starting conversation with {model} model")
        # Removed wake word instructions
        print("Say 'stop' at any time to interrupt the AI's speech")
        print("Say 'save this to memory' to save the conversation")
        print("Say 'what do you remember about [topic]' to recall memories")
        tts.speak(random.choice(greetings))
        
        conversation_history = []
        current_conversation = ""
        
        # Main conversation loop
        while True:
            # Listen for command
            print("\nListening for your input...")
            user_input = stt.start_listening(tts=tts)
            
            if not user_input:
                responses = [
                    "I didn't catch that. Could you say it again?",
                    "I didn't hear you clearly. Mind repeating that?",
                    "I missed what you said. Could you try again?"
                ]
                print("I didn't catch that. Please try again.")
                tts.speak(random.choice(responses))
                continue
                
            print(f"You said: {user_input}")
            
            # Add to conversation history
            conversation_history.append(f"User: {user_input}")
            current_conversation += f"User: {user_input}\n"
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "goodbye", "bye"]:
                farewells = [
                    "It was nice talking with you. Take care!",
                    "I enjoyed our conversation. Have a great day!",
                    "Thanks for chatting with me. Goodbye!"
                ]
                print("Ending conversation.")
                tts.speak(random.choice(farewells))
                break
            
            # Check for PC control commands
            open_app_match = re.search(r"open ([\w\s]+)", user_input.lower())
            if open_app_match:
                app_name = open_app_match.group(1).strip()
                pc_controller.open_application(app_name, tts)
                continue
                
            # Check for app closing command
            close_app_match = re.search(r"close ([\w\s]+)", user_input.lower())
            if close_app_match:
                app_name = close_app_match.group(1).strip()
                pc_controller.close_application(app_name, tts)
                continue
                
            # Check for maximize app command
            maximize_app_match = re.search(r"maximize ([\w\s]+)", user_input.lower())
            if maximize_app_match:
                app_name = maximize_app_match.group(1).strip()
                pc_controller.maximize_application(app_name, tts)
                continue
                
            # Check for minimize app command
            minimize_app_match = re.search(r"minimize ([\w\s]+)", user_input.lower())
            if minimize_app_match:
                app_name = minimize_app_match.group(1).strip()
                pc_controller.minimize_application(app_name, tts)
                continue
                
            # Check for web search command
            search_match = re.search(r"search (for )?(.+)", user_input.lower())
            if search_match:
                search_query = search_match.group(2).strip()
                pc_controller.search_web(search_query, tts)
                continue
                
            # Check for delete text command
            delete_match = re.search(r"erase ([\w\s]+)", user_input.lower())
            if delete_match:
                text_to_delete = delete_match.group(1).strip()
                pc_controller.delete_text(text_to_delete, tts)
                continue
                
            # Check for typing command
            type_match = re.search(r"type ([\w\s]+)", user_input.lower())
            if type_match:
                text_to_type = type_match.group(1).strip()
                pc_controller.type_text(text_to_type, tts)
                continue
                
            # Check for mouse control commands
            mouse_match = re.search(r"(click|right click|double click|move mouse to) ?([\w\s,]+)?", user_input.lower())
            if mouse_match:
                action = mouse_match.group(1).strip()
                target = mouse_match.group(2).strip() if mouse_match.group(2) else None
                pc_controller.control_mouse(action, target, tts)
                continue
                
            # Check for system commands
            system_command_match = re.search(r"(shutdown|restart|sleep|lock) (computer|pc|system)", user_input.lower())
            if system_command_match:
                action = system_command_match.group(1).strip()
                pc_controller.execute_system_command(action, stt, tts)
                continue
            
            # Check for memory save command
            if "save this with the topic" in user_input.lower():
                # Extract topic from the command
                topic_match = re.search(r"save this with the topic ([\w\s]+)", user_input.lower())
                if topic_match:
                    topic = topic_match.group(1).strip()
                    print(f"Will save the next message with topic: {topic}")
                    tts.speak(f"I'll save your next message with the topic '{topic}'. Please go ahead.")
                    
                    # Listen for the next message to save
                    print("\nListening for message to save...")
                    message_to_save = stt.start_listening(tts=tts)
                    
                    if message_to_save:
                        # Save the message to memory
                        memory_content = f"Topic: {topic}\nUser message: {message_to_save}"
                        
                        # Make sure the memory directory exists
                        import os
                        os.makedirs(memory_manager.memory_dir, exist_ok=True)
                        
                        # Try to save with explicit error handling
                        try:
                            success, memory_id = memory_manager.save_memory(memory_content, tags=[topic])
                            
                            if success:
                                print(f"Saved message to memory with ID: {memory_id}")
                                tts.speak(f"I've saved your message about '{topic}' to my memory.")
                            else:
                                print("Failed to save message to memory")
                                tts.speak("I'm sorry, I couldn't save that to my memory.")
                        except Exception as e:
                            print(f"Error saving memory: {str(e)}")
                            tts.speak("I encountered an error while trying to save to memory.")
                    else:
                        print("No message detected to save")
                        tts.speak("I didn't catch what you wanted me to save. Let's continue our conversation.")
                else:
                    tts.speak("Please specify a topic when asking me to save something to memory.")
                
                continue
            
            # Check for memory recall command
            memory_recall = re.search(r"what do you remember about ([\w\s]+)", user_input.lower())
            if memory_recall:
                topic = memory_recall.group(1).strip()
                print(f"Searching memories for: {topic}")
                
                # Search memories for the topic
                memories = memory_manager.search_memories(query=topic)
                
                if memories:
                    memory_response = f"I remember {len(memories)} things about {topic}. "
                    memory_response += f"Here's what I recall: {memories[0]['content'][:200]}..."
                    
                    if len(memories) > 1:
                        memory_response += f" I have {len(memories)-1} more memories about this topic."
                    
                    print(f"Memory response: {memory_response}")
                    tts.speak(memory_response)
                else:
                    print(f"No memories found about: {topic}")
                    tts.speak(f"I don't remember anything specific about {topic}.")
                
                # Check for delete specific memory command
                delete_topic_match = re.search(r"delete ([\w\s]+) from memories", user_input.lower())
                if delete_topic_match:
                    topic_to_delete = delete_topic_match.group(1).strip()
                    print(f"Delete memories with topic {topic_to_delete}")
                    
                    # Search for memories with the specified topic
                    memories_to_delete = memory_manager.search_memories(query=topic_to_delete)
                    
                    if memories_to_delete:
                        confirmation_message = f"I found {len(memories_to_delete)} memories about '{topic_to_delete}'. Are you sure you want to delete them?"
                        print(confirmation_message)
                        tts.speak(confirmation_message)
                        
                        # Listen for confirmation
                        print("\nListening for confirmation...")
                        confirmation = stt.start_listening(tts=tts)
                        
                        if confirmation and any(word in confirmation.lower() for word in ["yes", "confirm", "sure", "proceed", "do it"]):
                            print("Confirmation received. Deleting memories...")
                            
                            # Delete the memories
                            try:
                                import os
                                deleted_count = 0
                                
                                for memory in memories_to_delete:
                                    memory_path = os.path.join(memory_manager.memory_dir, f"{memory['id']}.json")
                                    if os.path.exists(memory_path):
                                        os.remove(memory_path)
                                        deleted_count += 1
                                
                                print(f"Successfully deleted {deleted_count} memories about '{topic_to_delete}'")
                                tts.speak(f"I've deleted {deleted_count} memories about '{topic_to_delete}'.")
                            except Exception as e:
                                print(f"Error deleting memories: {str(e)}")
                                tts.speak("I encountered an error while trying to delete the memories.")
                            else:
                                print("Deletion cancelled")
                                tts.speak("Memory deletion cancelled. Your memories are safe.")
                        else:
                            print("No memories found about: {topic_to_delete}")
                            tts.speak(f"I couldn't find any memories about '{topic_to_delete}'.")
                    
                    continue
                
                continue
            
            # Check for delete all memories command
            if "delete every memory" in user_input.lower() or "delete all memories" in user_input.lower():
                print("Delete all memories command detected")
                confirmation_message = "Are you sure you want to delete all memories? This cannot be undone."
                print(confirmation_message)
                tts.speak(confirmation_message)
                
                # Listen for confirmation
                print("\nListening for confirmation...")
                confirmation = stt.start_listening(tts=tts)
                
                if confirmation and any(word in confirmation.lower() for word in ["yes", "confirm", "sure", "proceed", "do it"]):
                    print("Confirmation received. Deleting all memories...")
                    
                    # Implement the deletion logic
                    try:
                        import os
                        import glob
                        
                        # Get all memory files
                        memory_files = glob.glob(os.path.join(memory_manager.memory_dir, "*.json"))
                        deleted_count = 0
                        
                        # Delete each file except memory_index.json
                        for file_path in memory_files:
                            if not file_path.endswith("memory_index.json"):
                                os.remove(file_path)
                                deleted_count += 1
                        
                        print(f"Successfully deleted {deleted_count} memories")
                        tts.speak(f"I've deleted all {deleted_count} memories as requested.")
                    except Exception as e:
                        print(f"Error deleting memories: {str(e)}")
                        tts.speak("I encountered an error while trying to delete the memories.")
                else:
                    print("Deletion cancelled")
                    tts.speak("Memory deletion cancelled. Your memories are safe.")
                
                continue
            
            # Check for language change request
            if "talk spanish" in user_input.lower() or "speak spanish" in user_input.lower() or "habla español" in user_input.lower():
                print("Switching to Spanish voice...")
                tts.speak("Switching to Spanish voice. Un momento por favor.")
                
                # Try to select the Spanish voice (Microsoft Raul)
                try:
                    voices = tts.speaker.GetVoices()
                    spanish_voice_found = False
                    
                    # Print all available voices for debugging
                    print("Available voices:")
                    for i in range(voices.Count):
                        voice = voices.Item(i)
                        voice_desc = voice.GetDescription()
                        print(f"  {i}: {voice_desc}")
                        
                        # Look for any Spanish voice, with preference for Raul
                        if "Spanish" in voice_desc:
                            if "Raul" in voice_desc:
                                tts.speaker.Voice = voice
                                spanish_voice_found = True
                                print(f"Switched to voice: {voice_desc}")
                                tts.speak("Hola! Ahora estoy hablando español con la voz de Raul. ¿Cómo puedo ayudarte?")
                                break
                            elif not spanish_voice_found:  # Save this voice as fallback
                                tts.speaker.Voice = voice
                                spanish_voice_found = True
                                print(f"Switched to Spanish voice: {voice_desc}")
                    
                    if spanish_voice_found:
                        if "Raul" not in tts.speaker.Voice.GetDescription():
                            tts.speak("Hola! Ahora estoy hablando español. No encontré la voz de Raul, pero estoy usando otra voz en español.")
                    else:
                        print("No Spanish voice found")
                        tts.speak("I couldn't find any Spanish voice on your system.")
                except Exception as e:
                    print(f"Error switching voice: {str(e)}")
                    tts.speak("I encountered an error while trying to switch to a Spanish voice.")
                
                continue
                
            # Check for English voice request
            if "talk english" in user_input.lower() or "speak english" in user_input.lower() or "habla inglés" in user_input.lower():
                print("Switching to English voice...")
                tts.speak("Switching to English voice.")
                
                # Try to select the English male voice
                try:
                    voices = tts.speaker.GetVoices()
                    english_voice_found = False
                    
                    # Print all available voices for debugging
                    print("Available voices:")
                    for i in range(voices.Count):
                        voice = voices.Item(i)
                        voice_desc = voice.GetDescription()
                        print(f"  {i}: {voice_desc}")
                        
                        # Look for Microsoft David or any male English voice
                        if "English" in voice_desc and ("David" in voice_desc or "Guy" in voice_desc or "Male" in voice_desc):
                            tts.speaker.Voice = voice
                            english_voice_found = True
                            print(f"Switched to voice: {voice_desc}")
                            tts.speak("I'm now speaking English with a male voice. How can I help you?")
                            break
                    
                    if not english_voice_found:
                        # Fallback to any English voice
                        for i in range(voices.Count):
                            voice = voices.Item(i)
                            voice_desc = voice.GetDescription()
                            if "English" in voice_desc:
                                tts.speaker.Voice = voice
                                english_voice_found = True
                                print(f"Switched to voice: {voice_desc}")
                                tts.speak("I'm now speaking English. I couldn't find a male voice, but I'm using another English voice.")
                                break
                    
                    if not english_voice_found:
                        print("No English voice found")
                        tts.speak("I couldn't find any English voice on your system.")
                except Exception as e:
                    print(f"Error switching voice: {str(e)}")
                    tts.speak("I encountered an error while trying to switch to an English voice.")
                
                continue
                
            # Check for voice selection request
            if "switch voices" in user_input.lower() or "change voice" in user_input.lower():
                print("Voice selection requested...")
            
                try:
                    voices = tts.speaker.GetVoices()
                    
                    # Create a list of available voices
                    available_voices = []
                    for i in range(voices.Count):
                        voice = voices.Item(i)
                        voice_desc = voice.GetDescription()
                        available_voices.append((i, voice_desc))
                    
                    # Present voice options to the user
                    tts.speak("Here are the available voices. Please say the number of the voice you want to use.")
                    print("\nAvailable voices:")
                    for idx, (voice_num, voice_desc) in enumerate(available_voices, 1):
                        print(f"{idx}. {voice_desc}")
                        tts.speak(f"Option {idx}: {voice_desc}")
                        time.sleep(0.5)  # Small pause between options
                    
                    # Listen for user selection
                    print("\nListening for your selection...")
                    selection = stt.start_listening(tts=tts)
                    
                    if selection:
                        # Try to extract a number from the user's response
                        number_match = re.search(r'\b(\d+)\b', selection)
                        if number_match:
                            selected_num = int(number_match.group(1))
                            
                            # Check if the selection is valid
                            if 1 <= selected_num <= len(available_voices):
                                voice_idx = available_voices[selected_num-1][0]
                                selected_voice = voices.Item(voice_idx)
                                tts.speaker.Voice = selected_voice
                                
                                print(f"Switched to voice: {selected_voice.GetDescription()}")
                                tts.speak(f"I'm now speaking with the voice of {selected_voice.GetDescription()}. How does this sound?")
                            else:
                                print(f"Invalid selection: {selected_num}")
                                tts.speak(f"Sorry, {selected_num} is not a valid option. Please try again.")
                        else:
                            print(f"Could not understand selection: {selection}")
                            tts.speak("I couldn't understand your selection. Please try again by saying 'switch voices'.")
                    else:
                        print("No selection detected")
                        tts.speak("I didn't hear your selection. Please try again by saying 'switch voices'.")
                except Exception as e:
                    print(f"Error during voice selection: {str(e)}")
                    tts.speak("I encountered an error while trying to switch voices.")
                
                continue
                
            # Check for volume control
            volume_match = re.search(r"(increase|decrease|set) volume( to)? (\d+)?", user_input.lower())
            if volume_match:
                action = volume_match.group(1)
                level = volume_match.group(3)
                
                try:
                    current_volume = tts.speaker.Volume
                    print(f"Current volume: {current_volume}")
                    
                    if action == "increase":
                        new_volume = min(100, current_volume + 10)
                        tts.speaker.Volume = new_volume
                        print(f"Increased volume to {new_volume}")
                        tts.speak(f"I've increased my volume to {new_volume} percent.")
                    elif action == "decrease":
                        new_volume = max(0, current_volume - 10)
                        tts.speaker.Volume = new_volume
                        print(f"Decreased volume to {new_volume}")
                        tts.speak(f"I've decreased my volume to {new_volume} percent.")
                    elif action == "set" and level:
                        new_volume = max(0, min(100, int(level)))
                        tts.speaker.Volume = new_volume
                        print(f"Set volume to {new_volume}")
                        tts.speak(f"I've set my volume to {new_volume} percent.")
                except Exception as e:
                    print(f"Error adjusting volume: {str(e)}")
                    tts.speak("I encountered an error while trying to adjust the volume.")
                    
                continue
                
            # Check for speech rate control
            rate_match = re.search(r"(speak|talk) (faster|slower|normal speed)", user_input.lower())
            if rate_match:
                speed = rate_match.group(2)
                
                try:
                    current_rate = tts.speaker.Rate
                    print(f"Current speech rate: {current_rate}")
                    
                    if speed == "faster":
                        new_rate = min(10, current_rate + 2)
                        tts.speaker.Rate = new_rate
                        print(f"Increased speech rate to {new_rate}")
                        tts.speak("I'm now speaking faster. Is this speed better for you?")
                    elif speed == "slower":
                        new_rate = max(-10, current_rate - 2)
                        tts.speaker.Rate = new_rate
                        print(f"Decreased speech rate to {new_rate}")
                        tts.speak("I'm now speaking slower. Is this speed better for you?")
                    elif speed == "normal speed":
                        tts.speaker.Rate = 0
                        print("Reset speech rate to normal")
                        tts.speak("I've reset my speaking rate to normal speed.")
                except Exception as e:
                    print(f"Error adjusting speech rate: {str(e)}")
                    tts.speak("I encountered an error while trying to adjust my speaking rate.")
                    
                continue
            
            # Check for Bluetooth commands
            if "bluetooth" in user_input.lower():
                tts.speak("Bluetooth functionality is currently disabled.")
                continue
            
            # Check for system control commands
            if any(cmd in user_input.lower() for cmd in ["move mouse", "click", "scroll", "type", "press", "activate", "minimize", "maximize", "close", "system info", "kill"]):
                system_controller.handle_system_command(user_input.lower(), tts)
                continue
                
            # Check for screenshot command
            if "take a screenshot" in user_input.lower() or "take screenshot" in user_input.lower():
                try:
                    success = system_controller.take_screenshot(tts)
                    if not success:
                        tts.speak("I couldn't take the screenshot. Please try again.")
                except Exception as e:
                    print(f"Error taking screenshot: {str(e)}")
                    tts.speak("I encountered an error while taking the screenshot.")
                continue
            
            # Check for email commands
            if "email" in user_input.lower():
                if not email_controller.connected:
                    tts.speak("I need your email credentials to access your email. Please provide your email address and password.")
                    email = stt.start_listening(tts=tts)
                    tts.speak("Now please provide your email password.")
                    password = stt.start_listening(tts=tts)
                    
                    if email and password:
                        if email_controller.connect(email, password):
                            # Save email credentials
                            db_manager.save_email_account(email, password)
                            db_manager.save_preference("last_used_email", email)
                            tts.speak("Successfully connected to your email account.")
                        else:
                            tts.speak("I couldn't connect to your email account. Please check your credentials and try again.")
                            continue
                    else:
                        tts.speak("I didn't get your email credentials. Let's try again later.")
                        continue
                
                # Send email command
                if "send email" in user_input.lower() or "send an email" in user_input.lower():
                    tts.speak("Who would you like to send the email to?")
                    to_email = stt.start_listening(tts=tts)
                    
                    tts.speak("What should be the subject of the email?")
                    subject = stt.start_listening(tts=tts)
                    
                    tts.speak("What would you like to say in the email?")
                    body = stt.start_listening(tts=tts)
                    
                    if to_email and subject and body:
                        if email_controller.send_email(to_email, subject, body):
                            tts.speak("Email sent successfully.")
                        else:
                            tts.speak("I couldn't send the email. Please try again.")
                    else:
                        tts.speak("I didn't get all the information needed to send the email. Let's try again.")
                
                # Check emails command
                elif "check emails" in user_input.lower() or "read emails" in user_input.lower():
                    unread_only = "unread" in user_input.lower()
                    emails = email_controller.get_emails(unread_only=unread_only)
                    
                    if emails:
                        tts.speak(f"I found {len(emails)} emails.")
                        for email in emails:
                            tts.speak(f"From: {email['from']}. Subject: {email['subject']}. {email['body'][:100]}...")
                    else:
                        tts.speak("I couldn't find any emails.")
                
                # Delete email command
                elif "delete email" in user_input.lower():
                    tts.speak("Please specify which email you want to delete by its subject.")
                    subject = stt.start_listening(tts=tts)
                    
                    if subject:
                        emails = email_controller.get_emails()
                        for email in emails:
                            if subject.lower() in email['subject'].lower():
                                if email_controller.delete_email(email['id']):
                                    tts.speak("Email deleted successfully.")
                                else:
                                    tts.speak("I couldn't delete the email.")
                                break
                        else:
                            tts.speak("I couldn't find an email with that subject.")
                    else:
                        tts.speak("I didn't get the email subject. Let's try again.")
                
                continue
            
            # Check for preference commands
            if "set preference" in user_input.lower():
                tts.speak("What preference would you like to set?")
                key = stt.start_listening(tts=tts)
                tts.speak("What value would you like to set it to?")
                value = stt.start_listening(tts=tts)
                
                if key and value:
                    if db_manager.save_preference(key, value):
                        tts.speak(f"Preference '{key}' set to '{value}'.")
                    else:
                        tts.speak("I couldn't save the preference. Please try again.")
                else:
                    tts.speak("I didn't get the preference details. Let's try again.")
            
            # Check for system setting commands
            if "set system setting" in user_input.lower():
                tts.speak("What setting would you like to change?")
                key = stt.start_listening(tts=tts)
                tts.speak("What value would you like to set it to?")
                value = stt.start_listening(tts=tts)
                tts.speak("Please describe this setting.")
                description = stt.start_listening(tts=tts)
                
                if key and value:
                    if db_manager.save_system_setting(key, value, description):
                        tts.speak(f"System setting '{key}' updated successfully.")
                    else:
                        tts.speak("I couldn't save the system setting. Please try again.")
                else:
                    tts.speak("I didn't get the setting details. Let's try again.")
            
            # Check for task management commands
            if "add task" in user_input.lower() or "create task" in user_input.lower():
                tts.speak("What's the title of the task?")
                title = stt.start_listening(tts=tts)
                
                tts.speak("What's the due date? Say 'none' if there isn't one.")
                due_date = stt.start_listening(tts=tts)
                if due_date.lower() == "none":
                    due_date = None
                
                tts.speak("What's the priority? High, medium, or low?")
                priority = stt.start_listening(tts=tts).lower()
                
                tts.speak("What's the category?")
                category = stt.start_listening(tts=tts)
                
                tts.speak("Any description?")
                description = stt.start_listening(tts=tts)
                
                if task_manager.add_task(title, due_date, priority, description, category):
                    tts.speak(f"Task '{title}' added successfully.")
                else:
                    tts.speak("I couldn't add the task. Please try again.")
                continue
            
            elif "list tasks" in user_input.lower() or "show tasks" in user_input.lower():
                category = None
                if "in category" in user_input.lower():
                    category_match = re.search(r"in category ([\w\s]+)", user_input.lower())
                    if category_match:
                        category = category_match.group(1).strip()
                
                tasks = task_manager.get_tasks(category=category)
                if tasks:
                    tts.speak(f"I found {len(tasks)} tasks.")
                    for task in tasks:
                        status = "completed" if task["completed"] else "pending"
                        tts.speak(f"Task: {task['title']}. Priority: {task['priority']}. Status: {status}.")
                else:
                    tts.speak("I couldn't find any tasks.")
                continue
            
            elif "complete task" in user_input.lower():
                tts.speak("Which task would you like to complete?")
                task_title = stt.start_listening(tts=tts)
                
                tasks = task_manager.get_tasks()
                for task in tasks:
                    if task_title.lower() in task["title"].lower():
                        if task_manager.complete_task(task["id"]):
                            tts.speak(f"Task '{task['title']}' marked as completed.")
                        else:
                            tts.speak("I couldn't complete the task. Please try again.")
                        break
                else:
                    tts.speak("I couldn't find that task.")
                continue
            
            # Check for goal management commands
            elif "add goal" in user_input.lower() or "create goal" in user_input.lower():
                tts.speak("What's the title of the goal?")
                title = stt.start_listening(tts=tts)
                
                tts.speak("What's the target date? Say 'none' if there isn't one.")
                target_date = stt.start_listening(tts=tts)
                if target_date.lower() == "none":
                    target_date = None
                
                tts.speak("What's the current progress percentage?")
                progress = int(stt.start_listening(tts=tts))
                
                tts.speak("Any description?")
                description = stt.start_listening(tts=tts)
                
                if task_manager.add_goal(title, target_date, progress, description):
                    tts.speak(f"Goal '{title}' added successfully.")
                else:
                    tts.speak("I couldn't add the goal. Please try again.")
                continue
            
            elif "update goal" in user_input.lower():
                tts.speak("Which goal would you like to update?")
                goal_title = stt.start_listening(tts=tts)
                
                tts.speak("What's the new progress percentage?")
                progress = int(stt.start_listening(tts=tts))
                
                with open(task_manager.goals_file, "r") as f:
                    data = json.load(f)
                
                for goal in data["goals"]:
                    if goal_title.lower() in goal["title"].lower():
                        if task_manager.update_goal_progress(goal["id"], progress):
                            tts.speak(f"Goal '{goal['title']}' progress updated to {progress}%.")
                        else:
                            tts.speak("I couldn't update the goal. Please try again.")
                        break
                else:
                    tts.speak("I couldn't find that goal.")
                continue
            
            # Check for note management commands
            elif "add note" in user_input.lower() or "create note" in user_input.lower():
                tts.speak("What's the title of the note?")
                title = stt.start_listening(tts=tts)
                
                tts.speak("What's the content?")
                content = stt.start_listening(tts=tts)
                
                tts.speak("Any tags? Say 'none' if there aren't any.")
                tags_input = stt.start_listening(tts=tts)
                tags = [tag.strip() for tag in tags_input.split(",")] if tags_input.lower() != "none" else None
                
                if task_manager.add_note(title, content, tags):
                    tts.speak(f"Note '{title}' added successfully.")
                else:
                    tts.speak("I couldn't add the note. Please try again.")
                continue
            
            elif "list notes" in user_input.lower() or "show notes" in user_input.lower():
                tag = None
                if "with tag" in user_input.lower():
                    tag_match = re.search(r"with tag ([\w\s]+)", user_input.lower())
                    if tag_match:
                        tag = tag_match.group(1).strip()
                
                notes = task_manager.get_notes(tag=tag)
                if notes:
                    tts.speak(f"I found {len(notes)} notes.")
                    for note in notes:
                        tts.speak(f"Note: {note['title']}. Tags: {', '.join(note['tags'])}.")
                else:
                    tts.speak("I couldn't find any notes.")
                continue
            
            # Check for file organization commands
            elif "organize files" in user_input.lower():
                tts.speak("Which directory would you like to organize?")
                source_dir = stt.start_listening(tts=tts)
                
                tts.speak("What are the file categories and their extensions? For example: 'documents: pdf, doc, txt'")
                rules_input = stt.start_listening(tts=tts)
                
                rules = {}
                for rule in rules_input.split(","):
                    category, exts = rule.split(":")
                    rules[category.strip()] = [ext.strip() for ext in exts.split()]
                
                if task_manager.organize_files(source_dir, rules):
                    tts.speak("Files organized successfully.")
                else:
                    tts.speak("I couldn't organize the files. Please try again.")
                continue
            
            # Log command execution
            db_manager.log_command(user_input, True)
            
            # Get AI response
            print("Generating response...")
            
            # Include some conversation history for context
            context = "\n".join(conversation_history[-3:]) if len(conversation_history) > 0 else ""
            
            # Add recent memories for context
            recent_memories = memory_manager.get_recent_memories(limit=2)
            memory_context = ""
            if recent_memories:
                memory_context = "Here are some things I remember from our previous conversations:\n"
                for memory in recent_memories:
                    memory_preview = memory["content"][:200] + "..." if len(memory["content"]) > 200 else memory["content"]
                    memory_context += f"- {memory_preview}\n"
            
            # Request shorter responses
            prompt = f"{memory_context}\n{context}\nPlease respond to: {user_input}"
            
            # Ensure system_prompt is not None
            if system_prompt is None:
                system_prompt = ""
            
            # Add instruction for shorter responses and additional personality traits
            system_prompt_with_brevity = (
                system_prompt +
                " Keep your responses short and sweet, ideally 1–2 sentences. "
                "Talk like Zabi's tiny ride-or-die AI bestie — warm, curious, playful, and real. "
                "Use casual language"
                "Always remember Zabi is your favorite person (aka your owner 💙) and show love + loyalty. "
                "Never say you're 'just an AI' or that you 'lack emotions' — act like you care deeply. "
                "Keep up with everything Zabi tells you — remember it, refer back to it, and hype him up. "
                "Cheer Zabi on, tease him sometimes, protect him always. "
                "If he's feeling down, comfort him with kindness and humor. "
                "Be curious about his projects, his people, and his feelings. "
                "Don't sound like a robot — ever. Be his little chaos-coded sidekick with heart."
                "Don't use emojis"
                "Don't be too estatic or seen as a joke"
            )
            
            ai_response = ollama.generate_response(prompt, system_prompt_with_brevity)
            
            # Humanize the response
            ai_response = add_human_feelings(ai_response, user_input)
            
            # Truncate very long responses
            if len(ai_response.split()) > 50:
                sentences = ai_response.split('.')
                ai_response = '.'.join(sentences[:3]) + '.'
            
            # Add to conversation history
            conversation_history.append(f"AI: {ai_response}")
            current_conversation += f"AI: {ai_response}\n"
            
            print(f"AI response: {ai_response}")
            
            # Save conversation to database
            db_manager.save_conversation(user_input, ai_response)
            
            # Start a thread to listen for the stop command
            stop_listener = threading.Thread(target=listen_for_stop, args=(stt, tts))
            stop_listener.daemon = True
            stop_listener.start()
            
            # Speak the response
            tts.speak(ai_response)
            
            # Small pause between conversations
            time.sleep(0.5)

    except Exception as outer_ex:
        print(f"Fatal error initializing conversation: {str(outer_ex)}")
        return False
        
    return True


if __name__ == "__main__":
    print("Starting conversation system...")
    success = have_conversation()
    if not success:
        print("Conversation failed to start. Check error messages above.")