# RagGit: Your Git Repository Intelligence Chatbot 🤖💬

<div align="center">

  <p><em>Ask questions about your code in natural language and get intelligent answers</em></p>
</div>

RagGit is an advanced web application that allows you to ask natural language questions about any Git repository and receive intelligent answers powered by Google's Gemini API. Using RAG (Retrieval Augmented Generation) techniques, RagGit analyzes your repository's code, history, and structure to provide contextual and accurate responses.

## ✨ Features

- **🔍 Git Repository Intelligence**: Ask questions about code functionality, architecture, dependencies, and more
- **💬 Interactive Chat Interface**: User-friendly interface to interact with your repository using natural language
- **🧠 Context-Aware Responses**: The bot provides reasoning context alongside answers
- **📝 Note-Taking**: Save important information from conversations for future reference
- **📂 Local Repository Management**: Clone and manage repositories directly from the UI
- **🧩 Comprehensive File Analysis**: Analyzes various file types and understands code patterns across multiple languages


## 🏗️ Project Structure

```
ragggit/
├── main.py                    # Flask application entry point
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
├── src/                      # Source code directory
│   ├── __init__.py
│   ├── agents/               # Agent definitions for different tasks
│   │   ├── __init__.py
│   │   └── agents.py         # CrewAI agent definitions
│   ├── config/               # Configuration settings
│   │   ├── __init__.py
│   │   └── settings.py       # Application settings and constants
│   ├── models/               # Core application models
│   │   ├── __init__.py
│   │   └── git_repo_bot.py   # Main GitRepoBot implementation
│   └── utils/                # Utility functions
│       ├── __init__.py
│       └── file_utils.py     # File handling utilities
└── templates/                # HTML templates
    ├── index.html            # Chat interface template
    └── landing.html          # Landing page template
```

## 🛠️ Technical Stack

- **🐍 Backend**: Python with Flask
- **🌐 Frontend**: HTML, CSS (with Tailwind CSS), JavaScript
- **🧠 AI**: Google's Gemini API via langchain-google-genai
- **👥 Agent Framework**: CrewAI for multi-agent collaboration
- **🔄 Repository Management**: GitPython for Git operations

## 🚀 Setup Instructions

### Prerequisites

- 🐍 Python 3.8+ installed
- 📚 Git installed
- 🔑 Google API key for Gemini API

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ariyha/raggit.git
   cd ragggit
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```


## 📖 Usage Guide

1. **🏠 Landing Page**: When you first open the application, you'll see the landing page where you can enter a Git repository URL.

2. **⚙️ Repository Setup**:
   - Enter a GitHub repository URL (e.g., `https://github.com/username/repo.git`)
   - Optionally, specify a local directory to store the repository
   - Click "Load Repository" to clone or update the repository

3. **💬 Chat Interface**:
   - After the repository is loaded, you'll be redirected to the chat interface
   - Ask questions about the repository in natural language
   - Examples:
     - "What does the main function do?"
     - "How is data being processed in this repository?"
     - "Explain the project structure"
     - "What are the key dependencies?"

4. **👁️ Viewing Context**:
   - Each response has a "Show Context" toggle to see the information sources used
   - This helps understand how the answer was derived


## 🔧 Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for the Gemini API
- Additional configuration can be found in `src/config/settings.py`

## 📦 Dependencies

Major dependencies include:
- 🤖 crewai >= 0.28.0
- 🔄 langchain-google-genai >= 0.0.5
- 🧠 langchain >= 0.1.0
- 🔮 google-generativeai >= 0.3.0
- 🗝️ python-dotenv >= 1.0.0
- 🌐 Flask (for web server)
- 📊 tqdm
- 🛜 GitPython (for Git operations)

## 👥 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

## 📄 License

[Add your license information here]

