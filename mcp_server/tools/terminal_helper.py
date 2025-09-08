import logging
import os
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def run_command(command: str, timeout: int = 30, cwd: str = None) -> dict[str, Any]:
    """Run a terminal command safely with timeout."""
    try:
        # Change to specified directory if provided
        original_cwd = os.getcwd()
        if cwd:
            os.chdir(cwd)

        result = subprocess.run(
            command.split() if isinstance(command, str) else command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Restore original directory
        if cwd:
            os.chdir(original_cwd)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": command,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
        }


def check_file_exists(filepath: str) -> dict[str, Any]:
    """Check if a file exists and get its info."""
    try:
        path = Path(filepath)
        if path.exists():
            stat = path.stat()
            return {
                "exists": True,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": str(path.absolute()),
            }
        else:
            return {
                "exists": False,
                "path": str(path.absolute()),
            }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e),
            "path": filepath,
        }


def read_file_safe(filepath: str, max_lines: int = 100) -> dict[str, Any]:
    """Safely read a file with line limit."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
            total_lines = len(lines)
            content_lines = lines[:max_lines]

            return {
                "success": True,
                "content": "".join(content_lines),
                "total_lines": total_lines,
                "displayed_lines": len(content_lines),
                "truncated": total_lines > max_lines,
                "filepath": filepath,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filepath": filepath,
        }


def list_directory_safe(directory: str, max_items: int = 50) -> dict[str, Any]:
    """Safely list directory contents with limit."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "error": f"Directory does not exist: {directory}",
                "directory": directory,
            }

        if not path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {directory}",
                "directory": directory,
            }

        items = []
        for item in path.iterdir():
            if len(items) >= max_items:
                break
            items.append(
                {
                    "name": item.name,
                    "is_file": item.is_file(),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0,
                },
            )

        return {
            "success": True,
            "items": items,
            "total_items": len(list(path.iterdir())),
            "displayed_items": len(items),
            "truncated": len(list(path.iterdir())) > max_items,
            "directory": str(path.absolute()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "directory": directory,
        }


def run_eval_safe(dataset: str, output_dir: str, timeout: int = 300) -> dict[str, Any]:
    """Safely run evaluation with proper error handling."""
    try:
        # Check if required files exist
        required_files = [
            "eval/run.py",
            "eval/configs/lab.yaml",
            dataset,
        ]

        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)

        if missing_files:
            return {
                "success": False,
                "error": f"Missing required files: {missing_files}",
                "missing_files": missing_files,
            }

        # Run evaluation
        cmd = [
            "python",
            "eval/run.py",
            "--dataset",
            dataset,
            "--output",
            output_dir,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(cmd),
            "output_dir": output_dir,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Evaluation timed out after {timeout} seconds",
            "command": " ".join(cmd),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": " ".join(cmd),
        }


def check_gates_safe(metrics_file: str) -> dict[str, Any]:
    """Safely check if gates pass using metrics file."""
    try:
        if not Path(metrics_file).exists():
            return {
                "success": False,
                "error": f"Metrics file does not exist: {metrics_file}",
                "metrics_file": metrics_file,
            }

        # Run gate check
        cmd = ["python", "scripts/ci/parse_metrics.py", metrics_file]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(cmd),
            "metrics_file": metrics_file,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Gate check timed out after 60 seconds",
            "command": " ".join(cmd),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": " ".join(cmd),
        }
