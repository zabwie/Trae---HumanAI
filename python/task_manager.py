import os
import json
import datetime
import shutil
from typing import List, Dict, Optional
import logging
from pathlib import Path

class TaskManager:
    def __init__(self, data_dir: str = "h:\\VSCodeProjects\\HumanAI\\python\\data"):
        self.data_dir = data_dir
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        self.goals_file = os.path.join(data_dir, "goals.json")
        self.notes_file = os.path.join(data_dir, "notes.json")
        self.log_file = os.path.join(data_dir, "action_log.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
        
        self.logger = logging.getLogger(__name__)
    
    def _init_files(self):
        """Initialize data files with empty structures"""
        default_data = {
            "tasks": [],
            "goals": [],
            "notes": [],
            "action_log": []
        }
        
        for file, key in [
            (self.tasks_file, "tasks"),
            (self.goals_file, "goals"),
            (self.notes_file, "notes"),
            (self.log_file, "action_log")
        ]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump({key: []}, f, indent=2)
    
    def add_task(self, title: str, due_date: Optional[str] = None, priority: str = "medium", 
                description: str = "", category: str = "general") -> bool:
        """Add a new task"""
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
            
            task = {
                "id": len(data["tasks"]) + 1,
                "title": title,
                "due_date": due_date,
                "priority": priority,
                "description": description,
                "category": category,
                "completed": False,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            data["tasks"].append(task)
            
            with open(self.tasks_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding task: {str(e)}")
            return False
    
    def get_tasks(self, category: Optional[str] = None, completed: bool = False) -> List[Dict]:
        """Get tasks, optionally filtered by category and completion status"""
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
            
            tasks = data["tasks"]
            if category:
                tasks = [t for t in tasks if t["category"] == category]
            if completed is not None:
                tasks = [t for t in tasks if t["completed"] == completed]
            
            return tasks
        except Exception as e:
            self.logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
            
            for task in data["tasks"]:
                if task["id"] == task_id:
                    task["completed"] = True
                    task["completed_at"] = datetime.datetime.now().isoformat()
                    break
            
            with open(self.tasks_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error completing task: {str(e)}")
            return False
    
    def add_goal(self, title: str, target_date: Optional[str] = None, 
                progress: int = 0, description: str = "") -> bool:
        """Add a new goal"""
        try:
            with open(self.goals_file, "r") as f:
                data = json.load(f)
            
            goal = {
                "id": len(data["goals"]) + 1,
                "title": title,
                "target_date": target_date,
                "progress": progress,
                "description": description,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            data["goals"].append(goal)
            
            with open(self.goals_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding goal: {str(e)}")
            return False
    
    def update_goal_progress(self, goal_id: int, progress: int) -> bool:
        """Update goal progress"""
        try:
            with open(self.goals_file, "r") as f:
                data = json.load(f)
            
            for goal in data["goals"]:
                if goal["id"] == goal_id:
                    goal["progress"] = progress
                    break
            
            with open(self.goals_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating goal: {str(e)}")
            return False
    
    def add_note(self, title: str, content: str, tags: List[str] = None) -> bool:
        """Add a new note"""
        try:
            with open(self.notes_file, "r") as f:
                data = json.load(f)
            
            note = {
                "id": len(data["notes"]) + 1,
                "title": title,
                "content": content,
                "tags": tags or [],
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            data["notes"].append(note)
            
            with open(self.notes_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding note: {str(e)}")
            return False
    
    def get_notes(self, tag: Optional[str] = None) -> List[Dict]:
        """Get notes, optionally filtered by tag"""
        try:
            with open(self.notes_file, "r") as f:
                data = json.load(f)
            
            notes = data["notes"]
            if tag:
                notes = [n for n in notes if tag in n["tags"]]
            
            return notes
        except Exception as e:
            self.logger.error(f"Error getting notes: {str(e)}")
            return []
    
    def edit_note(self, note_id: int, title: Optional[str] = None, 
                 content: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """Edit an existing note"""
        try:
            with open(self.notes_file, "r") as f:
                data = json.load(f)
            
            for note in data["notes"]:
                if note["id"] == note_id:
                    if title:
                        note["title"] = title
                    if content:
                        note["content"] = content
                    if tags is not None:
                        note["tags"] = tags
                    note["updated_at"] = datetime.datetime.now().isoformat()
                    break
            
            with open(self.notes_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error editing note: {str(e)}")
            return False
    
    def organize_files(self, source_dir: str, rules: Dict[str, List[str]]) -> bool:
        """Organize files based on rules"""
        try:
            for category, extensions in rules.items():
                category_dir = os.path.join(source_dir, category)
                os.makedirs(category_dir, exist_ok=True)
                
                for ext in extensions:
                    for file in Path(source_dir).glob(f"*.{ext}"):
                        if file.is_file():
                            shutil.move(str(file), os.path.join(category_dir, file.name))
            
            return True
        except Exception as e:
            self.logger.error(f"Error organizing files: {str(e)}")
            return False
    
    def log_action(self, action: str, details: Dict = None) -> bool:
        """Log an action or conversation"""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "action": action,
                "details": details or {}
            }
            
            data["action_log"].append(log_entry)
            
            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error logging action: {str(e)}")
            return False
    
    def get_action_log(self, limit: int = 10) -> List[Dict]:
        """Get recent action log entries"""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            
            return data["action_log"][-limit:]
        except Exception as e:
            self.logger.error(f"Error getting action log: {str(e)}")
            return [] 