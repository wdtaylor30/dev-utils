import sqlite3
import argparse
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('sqlite-demo')

CODE_BASE_DIR = Path.home() / "projects"
CODE_BASE_DIR.mkdir(parents=True, exist_ok=True) # Ensure the directory exists

def _get_absolute_and_validated_path(relative_path: str) -> Path:
    """
    Resolves a relative path to an absolute path within the CODE_BASE_DIR,
    raising an error if the resolved path is outside the allowed directory.
    """
    full_path = (CODE_BASE_DIR / relative_path).resolve()

    if not full_path.is_relative_to(CODE_BASE_DIR):
        raise ValueError(f"Access denied: '{relative_path}' resolves to a path outside the allowed directory: {CODE_BASE_DIR}")
    return full_path

@mcp.tool()
def read_file(file_path: str) -> str:
    """Reads the content of a file within the '~/projects' directory.

    Args:
        file_path (str): The path to the file, relative to '~/projects'.
                         Example: 'my_project/main.py'

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path points to a directory.
        ValueError: If the path is outside the allowed '~/projects' directory.
    """
    try:
        absolute_path = _get_absolute_and_validated_path(file_path)
        if absolute_path.is_dir():
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")
        if not absolute_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        return absolute_path.read_text()
    except ValueError as e:
        return f"Error: {e}"
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'."
    except IsADirectoryError:
        return f"Error: '{file_path}' is a directory. Use list_directory to explore it."
    except Exception as e:
        return f"An unexpected error occurred while reading file '{file_path}': {e}"


@mcp.tool()
def list_directory(directory_path: str = ".") -> list[str]:
    """Lists the contents of a directory within the '~/projects' directory.

    Args:
        directory_path (str, optional): The path to the directory, relative to '~/projects'.
                                        Defaults to the root of '~/projects'.
                                        Example: 'my_project/'

    Returns:
        list[str]: A list of file and directory names within the specified path.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path points to a file.
        ValueError: If the path is outside the allowed '~/projects' directory.
    """
    try:
        absolute_path = _get_absolute_and_validated_path(directory_path)
        if absolute_path.is_file():
            raise NotADirectoryError(f"'{directory_path}' is a file, not a directory.")
        if not absolute_path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        return [item.name for item in absolute_path.iterdir()]
    except ValueError as e:
        return [f"Error: {e}"]
    except FileNotFoundError:
        return [f"Error: Directory not found at '{directory_path}'."]
    except NotADirectoryError:
        return [f"Error: '{directory_path}' is a file. Use read_file to view its content."]
    except Exception as e:
        return [f"An unexpected error occurred while listing directory '{directory_path}': {e}"]


if __name__ == "__main__":
    print("Starting server... ")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)