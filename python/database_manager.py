import sqlite3
import json
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "ai_assistant.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()
        
    def _init_db(self) -> None:
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_input TEXT,
                        ai_response TEXT,
                        context TEXT
                    )
                ''')
                
                # Create user preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                
                # Create email accounts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE,
                        password TEXT,
                        smtp_server TEXT,
                        smtp_port INTEGER,
                        imap_server TEXT,
                        imap_port INTEGER,
                        last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create system settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        description TEXT
                    )
                ''')
                
                # Create command history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        command TEXT,
                        success BOOLEAN,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            
    def save_conversation(self, user_input: str, ai_response: str, context: Optional[Dict] = None) -> bool:
        """Save a conversation to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                context_json = json.dumps(context) if context else None
                
                cursor.execute('''
                    INSERT INTO conversations (user_input, ai_response, context)
                    VALUES (?, ?, ?)
                ''', (user_input, ai_response, context_json))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving conversation: {str(e)}")
            return False
            
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, timestamp, user_input, ai_response, context
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                conversations = []
                for row in cursor.fetchall():
                    context = json.loads(row[4]) if row[4] else None
                    conversations.append({
                        'id': row[0],
                        'timestamp': row[1],
                        'user_input': row[2],
                        'ai_response': row[3],
                        'context': context
                    })
                    
                return conversations
                
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return []
            
    def save_preference(self, key: str, value: Any) -> bool:
        """Save a user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                value_json = json.dumps(value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO preferences (key, value)
                    VALUES (?, ?)
                ''', (key, value_json))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving preference: {str(e)}")
            return False
            
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT value FROM preferences WHERE key = ?
                ''', (key,))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return default
                
        except Exception as e:
            self.logger.error(f"Error getting preference: {str(e)}")
            return default
            
    def save_email_account(self, email: str, password: str, 
                          smtp_server: str = "smtp.gmail.com",
                          smtp_port: int = 587,
                          imap_server: str = "imap.gmail.com",
                          imap_port: int = 993) -> bool:
        """Save email account credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO email_accounts 
                    (email, password, smtp_server, smtp_port, imap_server, imap_port)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email, password, smtp_server, smtp_port, imap_server, imap_port))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving email account: {str(e)}")
            return False
            
    def get_email_account(self, email: str) -> Optional[Dict]:
        """Get email account credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT email, password, smtp_server, smtp_port, imap_server, imap_port
                    FROM email_accounts
                    WHERE email = ?
                ''', (email,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'email': result[0],
                        'password': result[1],
                        'smtp_server': result[2],
                        'smtp_port': result[3],
                        'imap_server': result[4],
                        'imap_port': result[5]
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting email account: {str(e)}")
            return None
            
    def save_system_setting(self, key: str, value: Any, description: str = "") -> bool:
        """Save a system setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                value_json = json.dumps(value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value_json, description))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving system setting: {str(e)}")
            return False
            
    def get_system_setting(self, key: str, default: Any = None) -> Any:
        """Get a system setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT value FROM system_settings WHERE key = ?
                ''', (key,))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return default
                
        except Exception as e:
            self.logger.error(f"Error getting system setting: {str(e)}")
            return default
            
    def log_command(self, command: str, success: bool, error_message: Optional[str] = None) -> bool:
        """Log a command execution"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO command_history (command, success, error_message)
                    VALUES (?, ?, ?)
                ''', (command, success, error_message))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error logging command: {str(e)}")
            return False
            
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, timestamp, command, success, error_message
                    FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                commands = []
                for row in cursor.fetchall():
                    commands.append({
                        'id': row[0],
                        'timestamp': row[1],
                        'command': row[2],
                        'success': bool(row[3]),
                        'error_message': row[4]
                    })
                    
                return commands
                
        except Exception as e:
            self.logger.error(f"Error getting command history: {str(e)}")
            return [] 