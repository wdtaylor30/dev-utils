import os
from langchain.tools import tool
import json

# base directory where dean is safe
# to read and write.
# for me, ~/projects
# TODO: make this more configurable
BASE_DIR = os.path.join(os.path.expanduser('~'), "projects")

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file relative to BASE_DIR.
    Input should be a string representation of the
    relative path to the file."""
    full_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(full_path):
        return f"Error: File not found at {file_path}. Please check the path."
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return f"File content of {file_path}:\n ```\n{content}\n```"
    except Exception as e:
        return f"Error reading file {file_path}: {e}"

@tool # current setup doesn't take multi-argument tools
def write_file(json_file_info: str) -> str:
    """Writes contents to a file relative to BASE_DIR.
    Note that this overwrites existing files.
    Inputs:
        file_path (str): relative path to write to
        content (str): content to write"""
    try:
        data = json.loads(json_file_info)
        file_path = data.get('file_path')
        content = data.get('content')
        
        if not file_path:
            return f"Error: 'file_path' key is missing or empty in JSON input: {json_file_info}"
        if content is None: # missing, not empty
            return f"Error: 'content' key is missing in JSON input: {json_file_info}"
        
    except json.JSONDecodeError as e:
        return f"Error parsing JSON input for write_file: {e}. Input was '{json_file_info}'"
    except Exception as e:
        return f"Unexpected error processing input for write_file: {e}. Input was '{json_file_info}'"
    
    full_path = os.path.join(BASE_DIR, file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok = True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Sucessfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {e}"
@tool
def list_files(directory_path: str = ".") -> str:
    """Lists files and directories within a specified path, relative to BASE_DIR.
    Input:
        directory_path (str): relative path to directory
    Defaults to '.' for the current BASE_DIR."""
    full_path = os.path.join(BASE_DIR, directory_path)
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return f"Error: Directory not found or not a directory at {directory_path}."
    try:
        items = os.listdir(full_path)
        return f"Contents of {directory_path}:\n{', '.join(items)}"
    except Exception as e:
        return f"Error listing directory {directory_path}: {e}"

file_tools = [read_file, write_file, list_files]