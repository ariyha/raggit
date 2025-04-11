# GitRepoBot

A tool for query-focused analysis of Git repositories using AI agents.

## Overview

GitRepoBot is a Python application that uses AI agents to analyze Git repositories based on specific user queries. It identifies relevant files for a query, analyzes them, and provides comprehensive answers by synthesizing information from across the codebase.

## Features

- Query-based file selection to focus on relevant parts of the repository
- Smart file analysis that extracts only information related to the user's query
- Context aggregation to provide coherent answers from multiple files
- Efficient handling of large repositories with batched processing
- Caching to avoid redundant file reads

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory (see `.env.template` for format)
4. Add your Google API key to the `.env` file

## Usage

Basic usage:

```python
from src.models.git_repo_bot import GitRepoBot

# Initialize the bot with the path to your Git repository
repo_bot = GitRepoBot(repo_path="path/to/your/repository")

# Ask a question about the repository
response = repo_bot.answer_query("explain the purpose of file.js")
print(response)
```

## Project Structure

```
ragggit/
├── .env                     # Environment variables file
├── main.py                  # Entry point for the application
├── requirements.txt         # Dependencies
├── README.md                # Documentation
├── src/                     # Source code directory
│   ├── __init__.py          # Makes src a package
│   ├── config/              # Configuration
│   │   ├── __init__.py
│   │   └── settings.py      # Configuration settings
│   ├── models/              # Core models
│   │   ├── __init__.py
│   │   └── git_repo_bot.py  # Main GitRepoBot class
│   ├── agents/              # Agent definitions
│   │   ├── __init__.py
│   │   └── agents.py        # Agent creation functions
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── file_utils.py    # File handling utilities
```

## Requirements

- Python 3.8+
- Google API key with access to Gemini API

## License

MIT