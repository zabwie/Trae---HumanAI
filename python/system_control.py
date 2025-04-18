import pyautogui
import pygetwindow as gw
import os
import subprocess
import psutil
import keyboard
import mouse
import time
import re
import cv2
import numpy as np
from typing import Optional, Tuple, List
from PIL import Image
import pytesseract
import requests
from io import BytesIO
from datetime import datetime

class SystemController:
    def __init__(self):
        # Initialize pyautogui with safety features
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Initialize OpenCV
        self.template_cache = {}
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse to specified coordinates"""
        try:
            pyautogui.moveTo(x, y)
            return True
        except Exception as e:
            print(f"Error moving mouse: {str(e)}")
            return False
            
    def click(self, button: str = "left", x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Click mouse button at current position or specified coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            print(f"Error clicking mouse: {str(e)}")
            return False
            
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Double click at current position or specified coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y)
            else:
                pyautogui.doubleClick()
            return True
        except Exception as e:
            print(f"Error double clicking: {str(e)}")
            return False
            
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Right click at current position or specified coordinates"""
        return self.click("right", x, y)
        
    def scroll(self, amount: int) -> bool:
        """Scroll mouse wheel by specified amount"""
        try:
            pyautogui.scroll(amount)
            return True
        except Exception as e:
            print(f"Error scrolling: {str(e)}")
            return False
            
    def type_text(self, text: str) -> bool:
        """Type specified text"""
        try:
            pyautogui.write(text)
            return True
        except Exception as e:
            print(f"Error typing text: {str(e)}")
            return False
            
    def press_key(self, key: str) -> bool:
        """Press a single key"""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Error pressing key: {str(e)}")
            return False
            
    def hotkey(self, *keys: str) -> bool:
        """Press a combination of keys"""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"Error pressing hotkey: {str(e)}")
            return False
            
    def get_window(self, title: str) -> Optional[gw.Window]:
        """Get window by title"""
        try:
            return gw.getWindowsWithTitle(title)[0]
        except IndexError:
            return None
            
    def activate_window(self, title: str) -> bool:
        """Activate window by title"""
        try:
            window = self.get_window(title)
            if window:
                window.activate()
                return True
            return False
        except Exception as e:
            print(f"Error activating window: {str(e)}")
            return False
            
    def minimize_window(self, title: str) -> bool:
        """Minimize window by title"""
        try:
            window = self.get_window(title)
            if window:
                window.minimize()
                return True
            return False
        except Exception as e:
            print(f"Error minimizing window: {str(e)}")
            return False
            
    def maximize_window(self, title: str) -> bool:
        """Maximize window by title"""
        try:
            window = self.get_window(title)
            if window:
                window.maximize()
                return True
            return False
        except Exception as e:
            print(f"Error maximizing window: {str(e)}")
            return False
            
    def close_window(self, title: str) -> bool:
        """Close window by title"""
        try:
            window = self.get_window(title)
            if window:
                window.close()
                return True
            return False
        except Exception as e:
            print(f"Error closing window: {str(e)}")
            return False
            
    def get_active_window(self) -> Optional[gw.Window]:
        """Get currently active window"""
        try:
            return gw.getActiveWindow()
        except Exception as e:
            print(f"Error getting active window: {str(e)}")
            return None
            
    def get_all_windows(self) -> List[gw.Window]:
        """Get list of all windows"""
        try:
            return gw.getAllWindows()
        except Exception as e:
            print(f"Error getting windows: {str(e)}")
            return []
            
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        try:
            return pyautogui.size()
        except Exception as e:
            print(f"Error getting screen size: {str(e)}")
            return (0, 0)
            
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"Error getting mouse position: {str(e)}")
            return (0, 0)
            
    def run_command(self, command: str) -> Tuple[bool, str]:
        """Run a system command and return success status and output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return (result.returncode == 0, result.stdout)
        except Exception as e:
            print(f"Error running command: {str(e)}")
            return (False, str(e))
            
    def get_processes(self) -> List[psutil.Process]:
        """Get list of all running processes"""
        try:
            return list(psutil.process_iter())
        except Exception as e:
            print(f"Error getting processes: {str(e)}")
            return []
            
    def get_process_by_name(self, name: str) -> Optional[psutil.Process]:
        """Get process by name"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == name.lower():
                    return proc
            return None
        except Exception as e:
            print(f"Error getting process: {str(e)}")
            return None
            
    def kill_process(self, name: str) -> bool:
        """Kill process by name"""
        try:
            proc = self.get_process_by_name(name)
            if proc:
                proc.kill()
                return True
            return False
        except Exception as e:
            print(f"Error killing process: {str(e)}")
            return False
            
    def get_system_info(self) -> dict:
        """Get system information"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else None
            }
        except Exception as e:
            print(f"Error getting system info: {str(e)}")
            return {}
            
    def capture_screen(self) -> np.ndarray:
        """Capture the current screen"""
        try:
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error capturing screen: {str(e)}")
            return None
            
    def find_template(self, template_path: str, threshold: float = 0.8) -> List[Tuple[int, int, int, int]]:
        """Find template image on screen"""
        try:
            # Check cache first
            if template_path in self.template_cache:
                template = self.template_cache[template_path]
            else:
                template = cv2.imread(template_path)
                if template is None:
                    # Try to download from URL
                    response = requests.get(template_path)
                    template = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
                self.template_cache[template_path] = template
                
            screen = self.capture_screen()
            if screen is None:
                return []
                
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            matches = []
            for pt in zip(*locations[::-1]):
                matches.append((pt[0], pt[1], template.shape[1], template.shape[0]))
                
            return matches
        except Exception as e:
            print(f"Error finding template: {str(e)}")
            return []
            
    def find_text(self, text: str) -> List[Tuple[int, int, int, int]]:
        """Find text on screen using OCR"""
        try:
            screen = self.capture_screen()
            if screen is None:
                return []
                
            # Convert to grayscale
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            
            # Perform OCR
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            matches = []
            for i in range(len(data['text'])):
                if text.lower() in data['text'][i].lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    matches.append((x, y, w, h))
                    
            return matches
        except Exception as e:
            print(f"Error finding text: {str(e)}")
            return []
            
    def find_color(self, color: Tuple[int, int, int], tolerance: int = 30) -> List[Tuple[int, int]]:
        """Find specific color on screen"""
        try:
            screen = self.capture_screen()
            if screen is None:
                return []
                
            # Create color range
            lower = np.array([max(0, c - tolerance) for c in color])
            upper = np.array([min(255, c + tolerance) for c in color])
            
            # Find pixels within color range
            mask = cv2.inRange(screen, lower, upper)
            locations = np.where(mask > 0)
            
            return list(zip(locations[1], locations[0]))  # x, y coordinates
        except Exception as e:
            print(f"Error finding color: {str(e)}")
            return []
            
    def analyze_screen(self, tts) -> bool:
        """Analyze screen content and provide feedback"""
        try:
            screen = self.capture_screen()
            if screen is None:
                tts.speak("I couldn't capture the screen.")
                return False
                
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            
            # Get screen dimensions
            height, width = gray.shape
            
            # Analyze different regions
            regions = [
                (0, 0, width//2, height//2),  # Top-left
                (width//2, 0, width, height//2),  # Top-right
                (0, height//2, width//2, height),  # Bottom-left
                (width//2, height//2, width, height)  # Bottom-right
            ]
            
            # Check each region
            for i, (x1, y1, x2, y2) in enumerate(regions):
                region = gray[y1:y2, x1:x2]
                
                # Calculate average brightness
                brightness = np.mean(region)
                
                # Check for significant changes (potential movement)
                edges = cv2.Canny(region, 100, 200)
                edge_density = np.sum(edges > 0) / (region.size)
                
                # Look for text in the region
                text = pytesseract.image_to_string(region)
                
                # Provide feedback
                position = ["top-left", "top-right", "bottom-left", "bottom-right"][i]
                tts.speak(f"In the {position} region, I see {len(text.split())} words of text.")
                
                if edge_density > 0.1:
                    tts.speak(f"There seems to be some activity in the {position} region.")
                    
            return True
        except Exception as e:
            print(f"Error analyzing screen: {str(e)}")
            tts.speak("I encountered an error while analyzing the screen.")
            return False
            
    def take_screenshot(self, tts) -> bool:
        """Take a screenshot and save it with timestamp"""
        try:
            # Get current timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save the screenshot
            screenshot.save(filepath)
            
            # Provide feedback
            tts.speak(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            tts.speak("I encountered an error while taking the screenshot.")
            return False
            
    def handle_system_command(self, command: str, tts) -> bool:
        """Handle system-related commands"""
        command = command.lower()
        
        # Mouse control commands
        if "move mouse to" in command:
            # Extract coordinates from command
            match = re.search(r"move mouse to (\d+),?\s*(\d+)", command)
            if match:
                x, y = map(int, match.groups())
                return self.move_mouse(x, y)
                
        elif "click" in command:
            if "right" in command:
                return self.right_click()
            elif "double" in command:
                return self.double_click()
            else:
                return self.click()
                
        elif "scroll" in command:
            # Extract scroll amount
            match = re.search(r"scroll (up|down) (\d+)", command)
            if match:
                direction, amount = match.groups()
                amount = int(amount) * (-1 if direction == "up" else 1)
                return self.scroll(amount)
                
        # Keyboard commands
        elif "type" in command:
            # Extract text to type
            match = re.search(r"type (.+)", command)
            if match:
                text = match.group(1)
                return self.type_text(text)
                
        elif "press" in command:
            # Extract key to press
            match = re.search(r"press (.+)", command)
            if match:
                key = match.group(1)
                return self.press_key(key)
                
        # Window management commands
        elif "activate" in command:
            # Extract window title
            match = re.search(r"activate (.+)", command)
            if match:
                title = match.group(1)
                return self.activate_window(title)
                
        elif "minimize" in command:
            # Extract window title
            match = re.search(r"minimize (.+)", command)
            if match:
                title = match.group(1)
                return self.minimize_window(title)
                
        elif "maximize" in command:
            # Extract window title
            match = re.search(r"maximize (.+)", command)
            if match:
                title = match.group(1)
                return self.maximize_window(title)
                
        elif "close" in command:
            # Extract window title
            match = re.search(r"close (.+)", command)
            if match:
                title = match.group(1)
                return self.close_window(title)
                
        # System information commands
        elif "system info" in command:
            info = self.get_system_info()
            tts.speak(f"CPU usage is {info['cpu_percent']} percent. Memory usage is {info['memory_percent']} percent.")
            return True
            
        # Process management commands
        elif "kill" in command:
            # Extract process name
            match = re.search(r"kill (.+)", command)
            if match:
                name = match.group(1)
                return self.kill_process(name)
                
        # Screen analysis commands
        elif "can you see" in command or "find" in command:
            # Extract object to find
            match = re.search(r"(?:can you see|find) (?:a |the )?(.+)", command)
            if match:
                target = match.group(1).lower()
                
                # Try to find the object using different methods
                if target in ["rat", "mouse", "cat", "dog"]:
                    # Look for animal templates
                    template_path = f"templates/{target}.png"
                    matches = self.find_template(template_path)
                    if matches:
                        tts.speak(f"Yes, I found a {target} on the screen!")
                        return True
                    else:
                        tts.speak(f"No, I don't see any {target} on the screen.")
                        return True
                else:
                    # Try OCR for text
                    matches = self.find_text(target)
                    if matches:
                        tts.speak(f"Yes, I found '{target}' on the screen!")
                        return True
                    else:
                        tts.speak(f"No, I don't see '{target}' on the screen.")
                        return True
                        
        elif "analyze screen" in command or "what do you see" in command:
            return self.analyze_screen(tts)
            
        # Screenshot command
        elif "take a screenshot" in command or "take screenshot" in command:
            return self.take_screenshot(tts)
            
        return False 