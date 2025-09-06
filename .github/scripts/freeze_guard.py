#!/usr/bin/env python3
"""
Freeze guard script to prevent code changes during freeze periods.
Handles fork PRs by reading from GitHub event payload when available.
"""

import json
import os
import subprocess
import sys


def sha_or_default(env_key, default):
    """Get SHA from environment or return default."""
    v = os.environ.get(env_key)
    return v if v else default


def main():
    # Prefer event payload if present (Actions provides this JSON)
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    base = "origin/main"
    head = "HEAD"

    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, encoding="utf-8") as f:
                ev = json.load(f)
            pr = ev.get("pull_request") or {}
            base = pr.get("base", {}).get("sha") or base
            head = pr.get("head", {}).get("sha") or head
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            # Fallback to environment variables
            base = sha_or_default("GITHUB_BASE_REF", base)
            head = sha_or_default("GITHUB_SHA", head)
    else:
        base = sha_or_default("GITHUB_BASE_REF", base)
        head = sha_or_default("GITHUB_SHA", head)

    allowed = (
        ".cursor/",
        ".github/",
        "docs/",
        "README.md",
        "CHANGELOG.md",
        "pyproject.toml",
        "requirements",
        "requirements.txt",
        "requirements-dev.txt",
    )

    def changed_files():
        """Get list of changed files between base and head."""
        try:
            out = (
                subprocess.check_output(
                    ["git", "diff", "--name-only", f"{base}...{head}"], stderr=subprocess.PIPE
                )
                .decode()
                .splitlines()
            )
            return [p.strip() for p in out if p.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e.stderr.decode()}")
            return []

    bad = [p for p in changed_files() if not any(p.startswith(prefix) for prefix in allowed)]

    if bad:
        print("Freeze violated. Blocked paths:")
        print(json.dumps(bad, indent=2))
        sys.exit(1)

    print("Freeze respected.")


if __name__ == "__main__":
    main()
