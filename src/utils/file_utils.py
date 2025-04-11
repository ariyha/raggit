"""
Utility functions for file operations in the GitRepoBot application.
"""

import os
from pathlib import Path
from typing import Dict, List

from src.config.settings import EXCLUDED_DIRS, CODE_EXTENSIONS

def get_all_files(repo_path: str) -> Dict[str, str]:
    """
    Get all code files in the repository with their relative paths while efficiently skipping excluded directories.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        Dictionary mapping relative paths to full paths
    """
    print("Fetching all code files in the repository...")

    repo_path = Path(repo_path)
    file_paths = {}

    def scan_directory(directory: Path):
        """Recursively scan directory while skipping excluded folders."""
        try:
            for entry in os.scandir(directory):
                if entry.is_dir(follow_symlinks=False):
                    # Skip excluded directories
                    if entry.name in EXCLUDED_DIRS:
                        continue
                    scan_directory(Path(entry.path))  # Recursively scan subdirectory
                elif entry.is_file() and Path(entry.path).suffix in CODE_EXTENSIONS:
                    relative_path = Path(entry.path).relative_to(repo_path)
                    file_paths[str(relative_path)] = str(entry.path)
        except PermissionError:
            print(f"Skipping inaccessible directory: {directory}")

    scan_directory(repo_path)

    return file_paths

def read_file(file_path: str, file_cache: Dict[str, str] = None) -> str:
    """
    Read a file and return its content, using cache if available
    
    Args:
        file_path: Path to the file to read
        file_cache: Optional cache dictionary to store file contents
        
    Returns:
        File content as string
    """
    if file_cache is not None and file_path in file_cache:
        return file_cache[file_path]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Cache content if cache is provided
            if file_cache is not None:
                file_cache[file_path] = content
            return content
    except UnicodeDecodeError:
        try:
            # Try with a different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                if file_cache is not None:
                    file_cache[file_path] = content
                return content
        except Exception as e:
            return f"Error reading file: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_file_summaries(repo_path: str, file_cache: Dict[str, str] = None) -> Dict[str, Dict]:
    """
    Get a brief summary of each file (first few lines + size + extension)
    
    Args:
        repo_path: Path to the git repository
        file_cache: Optional cache dictionary to store file contents
        
    Returns:
        Dictionary with file summaries
    """
    file_paths = get_all_files(repo_path)
    print('Fetched all the code files')
    file_summaries = {}
    
    for relative_path, full_path in file_paths.items():
        try:
            content = read_file(full_path, file_cache)
            file_size = len(content)
            # Get first few lines (max 5) for a preview
            preview_lines = content.split('\n')[:10]
            preview = '\n'.join(preview_lines)
            
            # Truncate preview if it's too long
            if len(preview) > 1000:
                preview = preview[:1000] + "..."
            
            file_summaries[relative_path] = {
                "path": relative_path,
                "size": file_size,
                "extension": os.path.splitext(relative_path)[1],
                "preview": preview
            }
        except Exception as e:
            file_summaries[relative_path] = {
                "path": relative_path,
                "error": str(e)
            }
    
    return file_summaries