import os
from langchain.tools import tool

# base directory where dean is safe
# to read and write.
# for me, ~/projects
# TODO: make this more configurable
BASE_DIR = os.path("~/projects")

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file from BASE_DIR
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

# TODO: continue with Gemini response
