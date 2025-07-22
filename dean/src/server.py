import argparse
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import subprocess
import shlex


mcp = FastMCP('dean')

CODE_BASE_DIR = Path.home() / "projects"
CODE_BASE_DIR.mkdir(parents = True, exist_ok = True) 

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
def run_shell_command(command: str, cwd: str = ".") -> dict:
    """
    Run a shell command from a predefined list, within the defined sandbox.
    
    Args:
        command (str): The shell command to run.
        cwd (str): The current working directory
    
    Returns:
        A dictionary with outout, any error message or none at all, and a return code.
    """
    ALLOWED_COMMANDS = {
        "cd", "ls", "pwd", "cat", "grep", "find", "echo", "mkdir", "cp"
    }
    
    if not isinstance(command, str) or not command.strip():
        return {"stdout": "", "stderr": "Error: Command must be a non-empty string.", "returncode": 1}

    try:
        command_parts = shlex.split(command)
    except ValueError as e:
        return {"stdout": "", "stderr": f"Error parsing command: {e}", "returncode": 1}

    if not command_parts:
        return {"stdout": "", "stderr": "Error: Command is empty after parsing.", "returncode": 1}

    base_command = command_parts[0]

    if base_command not in ALLOWED_COMMANDS:
        return {"stdout": "", "stderr": f"Error: Command '{base_command}' is not allowed.", "returncode": 1}

    try:
        absolute_cwd = _get_absolute_and_validated_path(cwd)
        if not absolute_cwd.is_dir():
            raise NotADirectoryError(f"'{cwd}' is not a valid directory.")
    except (ValueError, NotADirectoryError) as e:
        return {"stdout": "", "stderr": f"Error: Invalid current working directory: {e}", "returncode": 1}

    try:
        result = subprocess.run(
            command_parts,
            cwd=absolute_cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Error: Command timed out after 10 seconds.", "returncode": 1}
    except FileNotFoundError:
        return {"stdout": "", "stderr": f"Error: Command '{base_command}' not found. Make sure it's installed and in PATH.", "returncode": 1}
    except Exception as e:
        return {"stdout": "", "stderr": f"An unexpected error occurred: {e}", "returncode": 1}


if __name__ == "__main__":
    print("Starting server... ")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)