# Trae - HumanAI

![Trae Logo](assets\trae_logo.png)

Trae is an advanced personal AI assistant that combines natural language processing, system control, and task management capabilities. It features voice interaction, memory management, and a wide range of system control functions.

## 🌟 Features

### 🗣️ Voice Interaction
- **Speech Recognition**: Uses Google Speech-to-Text for accurate voice input
- **Text-to-Speech**: Windows TTS with customizable voices and settings
- **Natural Conversation**: Human-like responses with emotional intelligence
- **Voice Commands**: Support for various system and task management commands

### 💻 System Control
- **Application Management**:
  - Open/close applications
  - Maximize/minimize windows
  - Search web
  - Type text
  - Control mouse (click, right-click, double-click, move)
- **System Commands**:
  - Shutdown/restart/sleep/lock computer
  - Take screenshots
  - Control volume
  - Adjust speech rate
- **Bluetooth Control**: Enable/disable Bluetooth functionality

### 📝 Task Management
- **Tasks**:
  - Create tasks with title, due date, priority, category, and description
  - List tasks (filtered by category)
  - Mark tasks as completed
- **Goals**:
  - Create goals with title, target date, progress, and description
  - Update goal progress
- **Notes**:
  - Create notes with title, content, and tags
  - List notes (filtered by tags)
- **File Organization**:
  - Organize files based on custom categories and extensions

### 🧠 Memory Management
- **Save Memories**: Store information with topics and tags
- **Recall Memories**: Retrieve information about specific topics
- **Delete Memories**: Remove specific memories or clear all memories

### 📧 Email Management
- **Email Access**:
  - Connect to email accounts (Gmail and other providers)
  - Send emails with attachments
  - Read emails (all or unread)
  - Delete emails
- **Security**: Secure storage of email credentials

### 💾 Database Management
- **Conversation History**: Store and retrieve conversation logs
- **User Preferences**: Save and manage user settings
- **System Settings**: Store system configuration
- **Action Logging**: Track system actions and commands

## 🚀 Getting Started

### Prerequisites
- Windows 10/11 operating system
- Python 3.8 or higher
- Administrator privileges (for system control features)
- Internet connection (for speech recognition and email features)
- Working microphone and speakers

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zabwie/Trae---HumanAI.git
   cd Trae---HumanAI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the program:
   ```bash
   python python/conversation.py
   ```

## 🎯 Voice Commands

### System Control
- "Open [application name]"
- "Close [application name]"
- "Maximize [application name]"
- "Minimize [application name]"
- "Search for [query]"
- "Type [text]"
- "Click [target]"
- "Right click [target]"
- "Double click [target]"
- "Move mouse to [target]"
- "Shutdown computer"
- "Restart computer"
- "Sleep computer"
- "Lock computer"
- "Take a screenshot"
- "Increase volume"
- "Decrease volume"
- "Set volume to [number]"
- "Speak faster"
- "Speak slower"
- "Talk normal speed"
- "Turn on Bluetooth"
- "Turn off Bluetooth"

### Task Management
- "Add task" or "Create task"
- "List tasks" or "Show tasks"
- "List tasks in category [category]"
- "Complete task"
- "Add goal" or "Create goal"
- "Update goal"
- "Add note" or "Create note"
- "List notes" or "Show notes"
- "List notes with tag [tag]"
- "Organize files"

### Memory Management
- "Save this with the topic [topic]"
- "What do you remember about [topic]"
- "Delete [topic] from memories"
- "Delete all memories" or "Delete every memory"

### Email Management
- "Send email" or "Send an email"
- "Check emails" or "Read emails"
- "Check unread emails"
- "Delete email"

### Voice Settings
- "Talk Spanish" or "Speak Spanish"
- "Talk English" or "Speak English"
- "Switch voices" or "Change voice"

## 🔧 Configuration

### First-Time Setup
1. Run the program for the first time
2. Follow the setup wizard for:
   - Microphone setup and testing
   - Voice selection and testing
   - Email account setup (if desired)
   - Basic permissions configuration

### Voice Calibration
- Speak clearly and at a normal pace
- Use the "Speak faster" or "Speak slower" commands to adjust the AI's speech rate
- Use "Increase volume" or "Decrease volume" to adjust the volume
- Try "Switch voices" to find your preferred voice

## ⚠️ Security Notes
- Email credentials are stored securely in the local database
- System control commands require appropriate permissions
- Bluetooth control may require administrator privileges
- Review the action log regularly
- Use strong passwords for email accounts

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Thanks to all contributors who have helped improve Trae
- Special thanks to the open-source community for their invaluable tools and libraries

## 📞 Support
For support, please open an issue in the GitHub repository or contact the maintainer.

---

Made with ❤️ by [zabwie](https://github.com/zabwie)