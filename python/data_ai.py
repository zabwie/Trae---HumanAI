import ollama
import json
import os
from datetime import datetime
import re
from typing import List, Dict, Any, Optional

class DataAI:
    def __init__(self, data_dir=None):
        # Use user's home directory if no specific directory is provided
        if data_dir is None:
            home_dir = os.path.expanduser("~")
            data_dir = os.path.join(home_dir, "HumanAI", "data")
        
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Create index file if it doesn't exist
        self.index_file = os.path.join(self.data_dir, "data_index.json")
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w") as f:
                json.dump({"data": []}, f)
        
        self.preferences_file = os.path.join(data_dir, "preferences.json")
        self.habits_file = os.path.join(data_dir, "habits.json")
        self.documents_file = os.path.join(data_dir, "documents.json")
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure all required data files exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        for file in [self.preferences_file, self.habits_file, self.documents_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({"data": []}, f)

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize any given text using AI.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            A concise summary of the text
        """
        try:
            prompt = f"Please summarize the following text in {max_length} characters or less:\n\n{text}"
            response = ollama.generate_response(prompt)
            return response.strip()
        except Exception as e:
            print(f"Error summarizing text: {str(e)}")
            return "Could not generate summary."

    def explain_document(self, text: str) -> Dict[str, Any]:
        """
        Explain a document by breaking it down into key points.
        
        Args:
            text: The document text to explain
            
        Returns:
            Dictionary containing key points, summary, and analysis
        """
        try:
            prompt = f"Please analyze this document and provide:\n1. Key points\n2. Main summary\n3. Technical terms explanation\n\nDocument:\n{text}"
            response = ollama.generate_response(prompt)
            
            # Parse the response into sections
            sections = response.split('\n\n')
            result = {
                "key_points": [],
                "summary": "",
                "technical_terms": {}
            }
            
            current_section = None
            for section in sections:
                if "key points" in section.lower():
                    current_section = "key_points"
                elif "summary" in section.lower():
                    current_section = "summary"
                elif "technical" in section.lower():
                    current_section = "technical_terms"
                
                if current_section == "key_points":
                    points = [p.strip('- ') for p in section.split('\n') if p.strip()]
                    result["key_points"].extend(points)
                elif current_section == "summary":
                    result["summary"] = section.strip()
                elif current_section == "technical_terms":
                    terms = section.split('\n')
                    for term in terms:
                        if ':' in term:
                            key, value = term.split(':', 1)
                            result["technical_terms"][key.strip()] = value.strip()
            
            return result
        except Exception as e:
            print(f"Error explaining document: {str(e)}")
            return {"error": "Could not analyze document"}

    def run_python_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in a safe environment.
        
        Args:
            code: The Python code to execute
            
        Returns:
            Dictionary containing output and any errors
        """
        try:
            # Create a safe environment with limited access
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                }
            }
            
            # Execute the code
            exec(code, safe_globals)
            
            return {
                "success": True,
                "output": "Code executed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def learn_preference(self, category: str, preference: str, value: Any):
        """
        Learn and store a user preference.
        
        Args:
            category: The category of the preference
            preference: The specific preference name
            value: The preference value
        """
        try:
            with open(self.preferences_file, 'r') as f:
                data = json.load(f)
            
            # Add timestamp
            entry = {
                "category": category,
                "preference": preference,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
            data["data"].append(entry)
            
            with open(self.preferences_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving preference: {str(e)}")

    def track_habit(self, habit: str, duration: int, notes: Optional[str] = None):
        """
        Track a user habit with duration and optional notes.
        
        Args:
            habit: The habit being tracked
            duration: Duration in minutes
            notes: Optional notes about the habit
        """
        try:
            with open(self.habits_file, 'r') as f:
                data = json.load(f)
            
            entry = {
                "habit": habit,
                "duration": duration,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            
            data["data"].append(entry)
            
            with open(self.habits_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error tracking habit: {str(e)}")

    def auto_categorize(self, text: str) -> List[str]:
        """
        Automatically categorize and tag text content.
        
        Args:
            text: The text to categorize
            
        Returns:
            List of categories and tags
        """
        try:
            prompt = f"Please analyze this text and suggest appropriate categories and tags:\n\n{text}"
            response = ollama.generate_response(prompt)
            
            # Extract categories and tags from the response
            categories = []
            tags = []
            
            # Look for patterns like "Category: X" or "Tags: X, Y, Z"
            category_match = re.search(r"Category:\s*([^\n]+)", response)
            if category_match:
                categories.append(category_match.group(1).strip())
            
            tags_match = re.search(r"Tags:\s*([^\n]+)", response)
            if tags_match:
                tags.extend([tag.strip() for tag in tags_match.group(1).split(',')])
            
            return {
                "categories": categories,
                "tags": tags
            }
        except Exception as e:
            print(f"Error categorizing text: {str(e)}")
            return {"categories": [], "tags": []}

    def get_preferences(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve user preferences, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of preference entries
        """
        try:
            with open(self.preferences_file, 'r') as f:
                data = json.load(f)
            
            if category:
                return [entry for entry in data["data"] if entry["category"] == category]
            return data["data"]
        except Exception as e:
            print(f"Error retrieving preferences: {str(e)}")
            return []

    def get_habits(self, habit: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve tracked habits, optionally filtered by habit name.
        
        Args:
            habit: Optional habit name to filter by
            
        Returns:
            List of habit entries
        """
        try:
            with open(self.habits_file, 'r') as f:
                data = json.load(f)
            
            if habit:
                return [entry for entry in data["data"] if entry["habit"] == habit]
            return data["data"]
        except Exception as e:
            print(f"Error retrieving habits: {str(e)}")
            return [] 