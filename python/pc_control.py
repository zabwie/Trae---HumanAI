import os
import subprocess
import ctypes
import time
import re
import sys
import logging

# Try to import optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available. App closing functionality will be limited.")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("pyautogui not available. Keyboard and mouse control will be disabled.")

class PCController:
    def __init__(self):
        logging.basicConfig(filename='pc_controller.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        # Dictionary mapping common app names to their executable paths
        self.app_paths = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "microsoft edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "notepad": r"C:\Windows\system32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "file explorer": r"C:\Windows\explorer.exe",
            "explorer": r"C:\Windows\explorer.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "command prompt": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "control panel": r"C:\Windows\System32\control.exe",
            "settings": r"C:\Windows\ImmersiveControlPanel\SystemSettings.exe",
            "task manager": r"C:\Windows\System32\taskmgr.exe",
            "discord": r"C:\Users\%USERNAME%\AppData\Local\Discord\app-*\Discord.exe",
            "spotify": r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
            "steam": r"C:\Program Files (x86)\Steam\steam.exe",
            "visual studio": r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
            "vs code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "visual studio code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        }
        
        # Dictionary mapping common app names to their process names
        self.app_process_names = {
            "chrome": ["chrome.exe"],
            "google chrome": ["chrome.exe"],
            "firefox": ["firefox.exe"],
            "edge": ["msedge.exe"],
            "microsoft edge": ["msedge.exe"],
            "word": ["WINWORD.EXE"],
            "excel": ["EXCEL.EXE"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "discord": ["Discord.exe", "Update.exe"],
            "spotify": ["Spotify.exe"],
            "steam": ["steam.exe"],
            "visual studio": ["devenv.exe"],
            "vs code": ["Code.exe"],
            "visual studio code": ["Code.exe"],
            "task manager": ["Taskmgr.exe"],
            "file explorer": ["explorer.exe"],
            "explorer": ["explorer.exe"]
        }
        
        # Expand environment variables in paths
        for key in self.app_paths:
            self.app_paths[key] = os.path.expandvars(self.app_paths[key])
    
    def is_admin(self):
        """Check if the script is running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def open_application(self, app_name, tts=None):
        """Open an application by name"""
        print(f"Attempting to open application: {app_name}")
        
        try:
            # Try to open with elevated privileges if needed
            if app_name in self.app_paths:
                path = self.app_paths[app_name]
                
                # Handle wildcard paths (like Discord)
                if "*" in path:
                    import glob
                    matching_paths = glob.glob(path)
                    if matching_paths:
                        path = matching_paths[0]  # Use the first match
                    else:
                        path = None
                
                if path and os.path.exists(path):
                    try:
                        # First try normal execution
                        subprocess.Popen(path, shell=True)
                        print(f"Opened {app_name}")
                        if tts:
                            tts.speak(f"Opening {app_name} for you, sir.")
                        return True
                    except Exception as e:
                        if "Access is denied" in str(e) and not self.is_admin():
                            print("Access denied, trying to run as administrator...")
                            if tts:
                                tts.speak(f"I need administrator privileges to open {app_name}. Please approve the prompt, sir.")
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)
                            return True
                        else:
                            raise
            
            # Try to find the app in common locations
            found = False
            
            # Try using the Windows Run command first (works for many apps)
            try:
                subprocess.Popen(["cmd", "/c", "start", app_name], shell=True)
                print(f"Attempted to open {app_name} using Windows Run")
                if tts:
                    tts.speak(f"I'm opening {app_name} for you, sir.")
                return True
            except:
                found = False
            
            # If not found, try common program locations
            if not found:
                program_locations = [
                    os.path.join(os.environ["ProgramFiles"], app_name),
                    os.path.join(os.environ["ProgramFiles(x86)"], app_name),
                    os.path.join(os.environ["APPDATA"], app_name),
                    os.path.join(os.environ["LOCALAPPDATA"], app_name),
                    # Search for .exe files with similar names
                    os.path.join(os.environ["ProgramFiles"], f"{app_name}.exe"),
                    os.path.join(os.environ["ProgramFiles(x86)"], f"{app_name}.exe"),
                    os.path.join(os.environ["LOCALAPPDATA"], "Programs", app_name)
                ]
                
                # Check if any of these locations exist
                for location in program_locations:
                    if os.path.exists(location):
                        try:
                            subprocess.Popen(location, shell=True)
                            found = True
                            print(f"Opened {app_name} from {location}")
                            if tts:
                                tts.speak(f"Opening {app_name} for you, sir.")
                            return True
                        except Exception as e:
                            if "Access is denied" in str(e) and not self.is_admin():
                                print("Access denied, trying to run as administrator...")
                                if tts:
                                    tts.speak(f"I need administrator privileges to open {app_name}. Please approve the prompt, sir.")
                                ctypes.windll.shell32.ShellExecuteW(None, "runas", location, None, None, 1)
                                found = True
                                return True
                            else:
                                continue
            
            if not found:
                print(f"Could not find or open {app_name}")
                if tts:
                    tts.speak(f"I'm sorry, sir. I couldn't find {app_name} on your system. Would you like me to search for it online?")
                return False
                
        except Exception as e:
            print(f"Error opening application: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to open {app_name}, sir.")
            return False
    
    def close_application(self, app_name, tts=None):
        """Close an application by name"""
        if not PSUTIL_AVAILABLE:
            if tts:
                tts.speak("I'm sorry, sir. The psutil module is not installed, so I cannot close applications.")
            return False
            
        print(f"Attempting to close application: {app_name}")
        
        try:
            # Try to find the process by name
            closed = False
            
            # Check if the app name is in our dictionary
            if app_name in self.app_process_names:
                process_names = self.app_process_names[app_name]
                for process_name in process_names:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'].lower() == process_name.lower():
                            proc.terminate()
                            closed = True
                            print(f"Closed {app_name} (process: {process_name})")
            
            # If not in dictionary, try to find by partial name match
            if not closed:
                for proc in psutil.process_iter(['pid', 'name']):
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        closed = True
                        print(f"Closed {proc.info['name']}")
            
            if closed:
                if tts:
                    tts.speak(f"I've closed {app_name} for you, sir.")
                return True
            else:
                print(f"Could not find {app_name} running")
                if tts:
                    tts.speak(f"I couldn't find {app_name} running on your system, sir.")
                return False
                
        except Exception as e:
            print(f"Error closing application: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to close {app_name}, sir.")
            return False
    
    def type_text(self, text, tts=None):
        """Type text using pyautogui"""
        if not PYAUTOGUI_AVAILABLE:
            if tts:
                tts.speak("I'm sorry, sir. The pyautogui module is not installed, so I cannot type text.")
            return False
            
        print(f"Attempting to type: {text}")
        
        try:
            # Give user a moment to focus the right window
            if tts:
                tts.speak(f"I'll type '{text}' in 3 seconds. Please focus the window where you want me to type.")
            time.sleep(3)
            
            # Type the text
            pyautogui.write(text)
            print(f"Typed: {text}")
            if tts:
                tts.speak(f"I've typed '{text}' for you, sir.")
            return True
        except Exception as e:
            print(f"Error typing text: {str(e)}")
            if tts:
                tts.speak("I encountered an error while trying to type, sir.")
            return False
    
    def control_mouse(self, action, target=None, tts=None):
        """Enhanced mouse control with coordinate validation"""
        if not PYAUTOGUI_AVAILABLE:
            self._speak_feedback(tts, "PyAutoGUI not available for mouse control.", "warning")
            return False
            
        try:
            screen_width, screen_height = pyautogui.size()
            if action == "click":
                if target:
                    if tts:
                        tts.speak(f"I'll try to find and click on {target}, sir.")
                    # This would require image recognition to find UI elements
                    # For now, just click at current position
                    pyautogui.click()
                else:
                    if tts:
                        tts.speak("Clicking at the current mouse position, sir.")
                    pyautogui.click()
            elif action == "right click":
                if tts:
                    tts.speak("Right-clicking at the current mouse position, sir.")
                pyautogui.rightClick()
            elif action == "double click":
                if tts:
                    tts.speak("Double-clicking at the current mouse position, sir.")
                pyautogui.doubleClick()
            elif action == "move mouse to":
                if target and "," in target:
                    # If coordinates are provided like "move mouse to 100,200"
                    coords = target.split(",")
                    if len(coords) == 2:
                        try:
                            x, y = int(coords[0]), int(coords[1])
                            pyautogui.moveTo(x, y, duration=0.5)
                            if tts:
                                tts.speak(f"Moved mouse to coordinates {x}, {y}, sir.")
                        except ValueError:
                            if tts:
                                tts.speak("I need numeric coordinates to move the mouse, sir.")
                            return False
                else:
                    if tts:
                        tts.speak(f"I need specific coordinates to move the mouse, sir.")
                    return False
            
            print(f"Performed mouse action: {action}")
            return True
        except Exception as e:
            print(f"Error controlling mouse: {str(e)}")
            if tts:
                tts.speak("I encountered an error while trying to control the mouse, sir.")
            return False
    
    def execute_system_command(self, action, stt=None, tts=None):
        """Execute system commands like shutdown, restart, etc."""
        print(f"System command requested: {action}")
        
        try:
            confirmation_message = f"Are you sure you want to {action} your computer, sir?"
            print(confirmation_message)
            if tts:
                tts.speak(confirmation_message)
            
            # Listen for confirmation
            confirmed = False
            if stt:
                print("\nListening for confirmation...")
                confirmation = stt.start_listening(tts=tts)
                
                if confirmation and any(word in confirmation.lower() for word in ["yes", "confirm", "sure", "proceed", "do it"]):
                    confirmed = True
            else:
                # If no speech-to-text available, assume confirmed
                confirmed = True
            
            if confirmed:
                print(f"Confirmation received. {action.capitalize()}ing computer...")
                if tts:
                    tts.speak(f"Confirmed. {action.capitalize()}ing your computer now, sir.")
                
                if action == "shutdown":
                    os.system("shutdown /s /t 10")
                    if tts:
                        tts.speak("Your computer will shut down in 10 seconds, sir.")
                elif action == "restart":
                    os.system("shutdown /r /t 10")
                    if tts:
                        tts.speak("Your computer will restart in 10 seconds, sir.")
                elif action == "sleep":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                    if tts:
                        tts.speak("Putting your computer to sleep, sir.")
                elif action == "lock":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                    if tts:
                        tts.speak("Locking your computer, sir.")
                return True
            else:
                print(f"{action.capitalize()} cancelled")
                if tts:
                    tts.speak(f"{action.capitalize()} cancelled, sir.")
                return False
        except Exception as e:
            print(f"Error executing system command: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to {action} your computer, sir.")
            return False

    def maximize_application(self, app_name, tts=None):
        """Maximize a running application window"""
        try:
            import win32gui
            import win32con
            
            # Dictionary mapping common app names to their window titles
            app_window_titles = {
                "chrome": ["Google Chrome"],
                "firefox": ["Mozilla Firefox"],
                "edge": ["Microsoft Edge"],
                "word": ["Document - Word", "Word"],
                "excel": ["Book - Excel", "Excel"],
                "notepad": ["Notepad"],
                "calculator": ["Calculator"],
                "discord": ["Discord"],
                "spotify": ["Spotify"],
                "visual studio": ["Microsoft Visual Studio"],
                "vs code": ["Visual Studio Code"],
                "file explorer": ["File Explorer"],
                "explorer": ["File Explorer"]
            }
            
            # Track if we found and maximized a window
            window_found = [False]
            
            # Function to maximize a window
            def maximize_window(hwnd, extra):
                if not win32gui.IsWindowVisible(hwnd):
                    return
                
                window_title = win32gui.GetWindowText(hwnd)
                if not window_title:
                    return
                
                # Check if window title contains the app name
                if app_name.lower() in window_title.lower():
                    print(f"Found window: {window_title}")
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    window_found[0] = True
                    return
                
                # Check if app name is in our dictionary
                if app_name in app_window_titles:
                    for title in app_window_titles[app_name]:
                        if title.lower() in window_title.lower():
                            print(f"Found window: {window_title}")
                            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                            window_found[0] = True
                            return
            
            # Try to find and maximize the window
            win32gui.EnumWindows(maximize_window, None)
            
            if window_found[0]:
                print(f"Successfully maximized {app_name}")
                if tts:
                    tts.speak(f"I've maximized {app_name} for you, sir.")
                return True
            else:
                print(f"Could not find {app_name} window to maximize")
                if tts:
                    tts.speak(f"I couldn't find {app_name} to maximize. Is it running?")
                    
        except Exception as e:
            print(f"Error maximizing application: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to maximize {app_name}.")
    
    def minimize_application(self, app_name, tts=None):
        """Minimize a running application window"""
        try:
            import win32gui
            import win32con
            
            # Dictionary mapping common app names to their window titles
            app_window_titles = {
                "chrome": ["Google Chrome"],
                "firefox": ["Mozilla Firefox"],
                "edge": ["Microsoft Edge"],
                "word": ["Document - Word", "Word"],
                "excel": ["Book - Excel", "Excel"],
                "notepad": ["Notepad"],
                "calculator": ["Calculator"],
                "discord": ["Discord"],
                "spotify": ["Spotify"],
                "visual studio": ["Microsoft Visual Studio"],
                "vs code": ["Visual Studio Code"],
                "file explorer": ["File Explorer"],
                "explorer": ["File Explorer"]
            }
            
            # Track if we found and minimized a window
            window_found = [False]
            
            # Function to minimize a window
            def minimize_window(hwnd, extra):
                if not win32gui.IsWindowVisible(hwnd):
                    return
                
                window_title = win32gui.GetWindowText(hwnd)
                if not window_title:
                    return
                
                # Check if window title contains the app name
                if app_name.lower() in window_title.lower():
                    print(f"Found window: {window_title}")
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    window_found[0] = True
                    return
                
                # Check if app name is in our dictionary
                if app_name in app_window_titles:
                    for title in app_window_titles[app_name]:
                        if title.lower() in window_title.lower():
                            print(f"Found window: {window_title}")
                            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                            window_found[0] = True
                            return
            
            # Try to find and minimize the window
            win32gui.EnumWindows(minimize_window, None)
            
            if window_found[0]:
                print(f"Successfully minimized {app_name}")
                if tts:
                    tts.speak(f"I've minimized {app_name} for you, sir.")
                return True
            else:
                print(f"Could not find {app_name} window to minimize")
                if tts:
                    tts.speak(f"I couldn't find {app_name} to minimize. Is it running?")
                    
        except Exception as e:
            print(f"Error minimizing application: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to minimize {app_name}.")
    
    def delete_text(self, amount, tts=None):
        """Delete text using backspace key"""
        if not PYAUTOGUI_AVAILABLE:
            if tts:
                tts.speak("I'm sorry, sir. The pyautogui module is not installed, so I cannot delete text.")
            return False
            
        print(f"Attempting to delete text: {amount}")
        
        try:
            # Parse the amount to delete
            if amount.lower() in ["all", "everything"]:
                # Select all text and delete it
                if tts:
                    tts.speak("I'll delete all text in 3 seconds. Please focus the correct window.")
                time.sleep(3)
                pyautogui.hotkey('ctrl', 'a')  # Select all
                pyautogui.press('delete')      # Delete selection
                print("Deleted all text")
                
            elif amount.lower() in ["word", "last word"]:
                # Delete the last word
                if tts:
                    tts.speak("I'll delete the last word in 3 seconds.")
                time.sleep(3)
                pyautogui.hotkey('ctrl', 'shift', 'left')  # Select last word
                pyautogui.press('delete')                  # Delete selection
                print("Deleted last word")
                
            elif amount.lower() in ["line", "current line"]:
                # Delete the current line
                if tts:
                    tts.speak("I'll delete the current line in 3 seconds.")
                time.sleep(3)
                pyautogui.hotkey('home')           # Go to beginning of line
                pyautogui.hotkey('shift', 'end')   # Select to end of line
                pyautogui.press('delete')          # Delete selection
                print("Deleted current line")
                
            elif amount.isdigit():
                # Delete specific number of characters
                num_chars = int(amount)
                if tts:
                    tts.speak(f"I'll delete {num_chars} characters in 3 seconds.")
                time.sleep(3)
                for _ in range(num_chars):
                    pyautogui.press('backspace')
                print(f"Deleted {num_chars} characters")
                
            else:
                # Try to delete the specific text if it's a phrase
                if tts:
                    tts.speak(f"I'll try to delete '{amount}' if I can find it. Please focus the correct window.")
                time.sleep(3)
                
                # First try to find and select the text
                # This is a basic implementation - press Ctrl+F to find
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.5)
                pyautogui.write(amount)
                time.sleep(0.5)
                pyautogui.press('escape')  # Close find dialog
                
                # Try to select and delete the text
                # This is approximate and may not work in all applications
                current_pos = pyautogui.position()
                pyautogui.click()  # Click where the search might have found the text
                for _ in range(len(amount)):
                    pyautogui.hotkey('shift', 'right')  # Select the text
                pyautogui.press('delete')  # Delete the selected text
                
                print(f"Attempted to delete '{amount}'")
            
            if tts:
                tts.speak(f"I've deleted the text for you, sir.")
            return True
            
        except Exception as e:
            print(f"Error deleting text: {str(e)}")
            if tts:
                tts.speak("I encountered an error while trying to delete text, sir.")
            return False

    def search_web(self, query, tts=None, browser="chrome"):
        """Enhanced web search with browser selection"""
        browsers = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        }
        try:
            import webbrowser
            import urllib.parse
            
            # Encode the search query for URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            print(f"Searching for: {query}")
            if tts:
                tts.speak(f"Searching the web for {query}")
            
            # Open Chrome with the search URL
            # Try to use Chrome specifically
            try:
                chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                webbrowser.get(chrome_path).open(search_url)
            except:
                # Fallback to default browser if Chrome isn't found
                webbrowser.open(search_url)
                
            return True
        except Exception as e:
            print(f"Error searching the web: {str(e)}")
            if tts:
                tts.speak(f"I encountered an error while trying to search for {query}")
            return False

    def _speak_feedback(self, tts, message, priority="normal"):
        """Improved voice feedback with priority levels"""
        if tts:
            try:
                if priority == "warning":
                    tts.speaker.Rate = -2  # Slower for important messages
                tts.speak(message)
                if priority == "warning":
                    tts.speaker.Rate = 0  # Reset to normal speed
            except Exception as e:
                self.logger.error(f"TTS error: {str(e)}")

    def _resolve_app_path(self, app_name):
        """Dynamically resolve application paths using Windows Registry"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
            path, _ = winreg.QueryValueEx(key, f"{app_name}.exe")
            return path
        except Exception as e:
            self.logger.warning(f"Could not resolve path for {app_name}: {str(e)}")
            return None

    def _update_running_apps(self):
        """Update the dictionary of running applications"""
        if PSUTIL_AVAILABLE:
            self.running_apps = {proc.info['name']: proc.info['pid'] 
                               for proc in psutil.process_iter(['pid', 'name'])}

    def get_cpu_percent(self, tts=None):
        """Get current CPU usage percentage"""
        if not PSUTIL_AVAILABLE:
            self._speak_feedback(tts, "Psutil not available for CPU stats.", "warning")
            return None

        try:
            percent = psutil.cpu_percent(interval=1)
            if tts:
                tts.speak(f"Current CPU usage is {percent} percent, sir.")
            return percent
        except Exception as e:
            self.logger.error(f"CPU monitoring error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the CPU usage, sir.")
            return None

    def get_memory_percent(self, tts=None):
        """Get current memory usage percentage"""
        if not PSUTIL_AVAILABLE:
            self._speak_feedback(tts, "Psutil not available for memory stats.", "warning")
            return None

        try:
            percent = psutil.virtual_memory().percent
            if tts:
                tts.speak(f"Current memory usage is {percent} percent, sir.")
            return percent
        except Exception as e:
            self.logger.error(f"Memory monitoring error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the memory usage, sir.")
            return None

    def get_disk_percent(self, tts=None, drive='C:'):
        """Get current disk usage percentage for specified drive"""
        if not PSUTIL_AVAILABLE:
            self._speak_feedback(tts, "Psutil not available for disk stats.", "warning")
            return None

        # Ensure drive is in correct format for psutil (e.g., 'C:\\')
        if not drive.endswith('\\'):
            drive = drive + '\\'

        try:
            percent = psutil.disk_usage(drive).percent
            if tts:
                tts.speak(f"Current disk usage on {drive} is {percent} percent, sir.")
            return percent
        except Exception as e:
            self.logger.error(f"Disk monitoring error: {str(e)}")
            if tts:
                tts.speak(f"I couldn't check the disk usage on {drive}, sir.")
            return None

    def get_system_stats(self, tts=None):
        """Get comprehensive system statistics"""
        if not PSUTIL_AVAILABLE:
            self._speak_feedback(tts, "Psutil not available for system stats.", "warning")
            return None

        try:
            # Don't pass tts to sub-methods to avoid double-speaking
            cpu = self.get_cpu_percent()
            memory = self.get_memory_percent()
            disk = self.get_disk_percent()
            stats = {
                "cpu": cpu,
                "memory": memory,
                "disk": disk
            }
            if tts:
                tts.speak(
                    f"System status: CPU at {cpu if cpu is not None else 'unknown'} percent, "
                    f"memory at {memory if memory is not None else 'unknown'} percent, "
                    f"and disk at {disk if disk is not None else 'unknown'} percent usage, sir."
                )
            return stats
        except Exception as e:
            self.logger.error(f"System stats error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the system status, sir.")
            return None

    def clipboard_control(self, action, text=None, tts=None):
        """Control clipboard operations"""
        try:
            import pyperclip
            if action == "copy" and text:
                pyperclip.copy(text)
            elif action == "paste":
                return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"Clipboard error: {str(e)}")
            self._speak_feedback(tts, "Clipboard operation failed.", "warning")

    def get_cpu_info(self, tts=None):
        """Get CPU model and usage percentage"""
        try:
            import platform
            cpu_name = platform.processor()
            usage = psutil.cpu_percent(interval=1) if PSUTIL_AVAILABLE else None
            if tts:
                if cpu_name:
                    tts.speak(f"Your CPU is {cpu_name}, and current usage is {usage if usage is not None else 'unknown'} percent, sir.")
                else:
                    tts.speak("I could not detect your CPU, sir.")
            return {"name": cpu_name, "usage": usage}
        except Exception as e:
            self.logger.error(f"CPU info error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the CPU information, sir.")
            return None

    def get_memory_info(self, tts=None):
        """Get RAM total, available, and usage percentage"""
        try:
            if not PSUTIL_AVAILABLE:
                self._speak_feedback(tts, "Psutil not available for memory info.", "warning")
                return None
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            percent = mem.percent
            if tts:
                tts.speak(
                    f"Your system has {total_gb:.1f} gigabytes of RAM, "
                    f"{available_gb:.1f} gigabytes available, "
                    f"and current usage is {percent} percent, sir."
                )
            return {"total_gb": total_gb, "available_gb": available_gb, "usage": percent}
        except Exception as e:
            self.logger.error(f"Memory info error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the memory information, sir.")
            return None

    def get_disk_info(self, tts=None, drive='C:'):
        """Get disk model (if possible), total, used, free, and usage percentage"""
        try:
            if not PSUTIL_AVAILABLE:
                self._speak_feedback(tts, "Psutil not available for disk info.", "warning")
                return None
            # Ensure drive is in correct format for psutil (e.g., 'C:\\')
            if not drive.endswith('\\'):
                drive = drive + '\\'
            usage = psutil.disk_usage(drive)
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            free_gb = usage.free / (1024 ** 3)
            percent = usage.percent
            # Disk model is not easily available via psutil; would require wmi
            try:
                import wmi
                c = wmi.WMI()
                for disk in c.Win32_LogicalDisk():
                    if disk.DeviceID == drive.rstrip('\\'):
                        model = disk.VolumeName or "Unknown"
                        break
                else:
                    model = "Unknown"
            except Exception:
                model = "Unknown"
            if tts:
                tts.speak(
                    f"Your {drive} drive is {model}. "
                    f"Total size is {total_gb:.1f} gigabytes, "
                    f"{free_gb:.1f} gigabytes free, "
                    f"and current usage is {percent} percent, sir."
                )
            return {"model": model, "total_gb": total_gb, "used_gb": used_gb, "free_gb": free_gb, "usage": percent}
        except Exception as e:
            self.logger.error(f"Disk info error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the disk information, sir.")
            return None

    def get_gpu_info(self, tts=None):
        """Get GPU model and usage (if available) using WMI and nvidia-smi if present"""
        try:
            import wmi
            w = wmi.WMI()
            gpus = w.Win32_VideoController()
            gpu_names = [gpu.Name for gpu in gpus]
            usage = None
            # Try to get usage via nvidia-smi if available
            try:
                import subprocess
                result = subprocess.check_output(
                    ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                    encoding='utf-8'
                )
                usage = int(result.strip().split('\n')[0])
            except Exception:
                usage = None
            if tts:
                if gpu_names:
                    usage_str = f" and current usage is {usage} percent" if usage is not None else ""
                    tts.speak(f"Your GPU is: {', '.join(gpu_names)}{usage_str}, sir.")
                else:
                    tts.speak("I could not detect your GPU, sir.")
            return {"name": gpu_names, "usage": usage}
        except ImportError:
            if tts:
                tts.speak("The wmi module is not installed, so I cannot check your GPU model, sir.")
            return None
        except Exception as e:
            self.logger.error(f"GPU info error: {str(e)}")
            if tts:
                tts.speak("I couldn't check the GPU information, sir.")
            return None
import tkinter as tk
import threading
import time

class AssistantOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assistant Overlay")
        self.root.configure(bg="#181818")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(self._center_window(400, 400))
        self.root.wm_attributes("-transparentcolor", "#181818")
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="#181818", highlightthickness=0)
        self.canvas.pack()
        self.circle = None
        self.state = "idle"  # idle, user, ai
        self._draw_circle(200, 200, 60, "#444")
        self.anim_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.anim_thread.start()

    def _center_window(self, w, h):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        return f"{w}x{h}+{x}+{y}"

    def _draw_circle(self, x, y, r, color):
        if self.circle:
            self.canvas.delete(self.circle)
        self.circle = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

    def set_state(self, state):
        """Set the overlay state: 'idle', 'user', or 'ai'"""
        self.state = state

    def _animation_loop(self):
        while True:
            if self.state == "user":
                # Glow effect
                for i in range(10, 31, 2):
                    self._draw_circle(200, 200, 60, f"#{30+i:02x}{30+i:02x}{60+i:02x}")
                    self.root.update()
                    time.sleep(0.01)
                for i in range(30, 9, -2):
                    self._draw_circle(200, 200, 60, f"#{30+i:02x}{30+i:02x}{60+i:02x}")
                    self.root.update()
                    time.sleep(0.01)
            elif self.state == "ai":
                # Inflate/deflate effect
                for r in range(60, 90, 2):
                    self._draw_circle(200, 200, r, "#2e8bff")
                    self.root.update()
                    time.sleep(0.01)
                for r in range(90, 59, -2):
                    self._draw_circle(200, 200, r, "#2e8bff")
                    self.root.update()
                    time.sleep(0.01)
            else:
                self._draw_circle(200, 200, 60, "#444")
                self.root.update()
                time.sleep(0.05)

    def show(self):
        self.root.mainloop()