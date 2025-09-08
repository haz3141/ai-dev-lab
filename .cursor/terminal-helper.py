#!/usr/bin/env python3
"""Terminal Memory Helper - Prevents getting stuck in interactive commands"""

import json
import subprocess
import sys
from pathlib import Path


class TerminalMemory:
    def __init__(self, memory_file=".cursor/terminal-memory.json"):
        self.memory_file = Path(memory_file)
        self.memory = self.load_memory()

    def load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "last_command": "",
            "last_exit_code": 0,
            "last_working_directory": str(Path.cwd()),
            "command_timeout": 10,
            "stuck_commands": [],
            "safe_commands": [],
            "last_successful_commands": [],
        }

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def is_stuck_command(self, command):
        """Check if command is likely to hang"""
        stuck_patterns = [
            "python -m",
            "uvicorn",
            "jupyter",
            "ipython",
            "python -i",
            "bash -i",
            "zsh -i",
            "interactive",
        ]
        return any(pattern in command.lower() for pattern in stuck_patterns)

    def is_safe_command(self, command):
        """Check if command is safe to run without timeout"""
        safe_patterns = [
            "git status",
            "git log",
            "ls",
            "pwd",
            "echo",
            "cat",
            "head",
            "tail",
            "grep",
            "find",
            "which",
            "python --version",
        ]
        return any(pattern in command.lower() for pattern in safe_patterns)

    def run_with_timeout(self, command, timeout=None, cwd=None):
        """Run command with timeout protection"""
        if timeout is None:
            timeout = self.memory.get("command_timeout", 10)

        if cwd is None:
            cwd = self.memory.get("last_working_directory", ".")

        # Check if command is likely to hang
        if self.is_stuck_command(command):
            print(f"⚠️  Command '{command}' may hang - using timeout {timeout}s")
            return self._run_with_signal_timeout(command, timeout, cwd)
        elif self.is_safe_command(command):
            return self._run_safe(command, cwd)
        else:
            return self._run_with_signal_timeout(command, timeout, cwd)

    def _run_safe(self, command, cwd):
        """Run safe commands without timeout"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30,  # Still use a reasonable timeout
            )
            self.memory["last_command"] = command
            self.memory["last_exit_code"] = result.returncode
            self.memory["last_working_directory"] = cwd
            self.save_memory()
            return result
        except subprocess.TimeoutExpired:
            print(f"❌ Command timed out after 30s: {command}")
            return None

    def _run_with_signal_timeout(self, command, timeout, cwd):
        """Run command with signal-based timeout"""
        try:
            # Use timeout command if available
            timeout_cmd = f"timeout {timeout} {command}"
            result = subprocess.run(
                timeout_cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            self.memory["last_command"] = command
            self.memory["last_exit_code"] = result.returncode
            self.memory["last_working_directory"] = cwd
            self.save_memory()
            return result
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python terminal-helper.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    memory = TerminalMemory()

    print(f"🚀 Running: {command}")
    result = memory.run_with_timeout(command)

    if result is None:
        print("❌ Command failed or timed out")
        sys.exit(1)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
