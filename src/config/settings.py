"""
Configuration settings for the GitRepoBot application.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Default model settings
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.2

# File handling settings
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200

# Excluded directories for file scanning
EXCLUDED_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv', 'dist', 'build'}

# Code file extensions to include
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.cs', '.go', 
    '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.sh', '.md', '.json', '.yaml', 
    '.yml', '.html', '.css', '.scss', '.sql', '.graphql', '.proto'
}