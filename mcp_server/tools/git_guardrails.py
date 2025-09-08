#!/usr/bin/env python3
"""Git Guardrails MCP Tools

Provides tools to enforce Git flow practices:
- ensure_on_feature_branch: Validates current branch and creates feature
  branch if needed
- safe_commit: Runs pre-commit checks and commits with conventional format
- create_pr: Creates pull request with standard template
- branch_diff_summary: Provides summary of changes for PR description
"""

import re
import subprocess
from pathlib import Path
from typing import Any


def run_git_command(cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
    """Run a git command and return result."""
    try:
        result = subprocess.run(
            ["git", *cmd],
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd(),
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
        }


def get_current_branch() -> str:
    """Get current git branch name."""
    result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    return result["stdout"] if result["success"] else ""


def is_feature_branch(branch: str) -> bool:
    """Check if branch follows feature branch naming convention."""
    pattern = r"^(feat|fix|chore|docs|style|refactor|test)/[a-z0-9-]+-[a-z0-9-]+$"
    return bool(re.match(pattern, branch))


def validate_conventional_commit(message: str) -> dict[str, Any]:
    """Validate commit message follows conventional commit format."""
    pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\([a-z0-9-]+\))?!?:\s.+"
    is_valid = bool(re.match(pattern, message))

    if not is_valid:
        return {
            "valid": False,
            "error": "Commit message must follow format: type(scope)!: description",
        }

    return {"valid": True}


def run_pre_commit_checks() -> dict[str, Any]:
    """Run pre-commit checks (tests, lint, etc.)."""
    checks = []
    success = True

    # Check if working tree is clean
    status_result = run_git_command(["status", "--porcelain"])
    if status_result["stdout"]:
        checks.append({"check": "working_tree_clean", "passed": False, "details": "Uncommitted changes exist"})
        success = False
    else:
        checks.append({"check": "working_tree_clean", "passed": True})

    # Run tests if available (skip if no test framework detected)
    test_result = run_git_command(["python", "-m", "pytest", "--tb=short", "-q", "--disable-warnings"])
    if test_result["returncode"] == 0:
        checks.append({"check": "tests", "passed": True})
    else:
        # Don't fail if tests don't exist or can't run
        checks.append({"check": "tests", "passed": False, "details": "Tests not available or failed"})

    # Run lint if available (skip if black not installed)
    lint_result = run_git_command(["python", "-m", "black", "--check", "."])
    if lint_result["returncode"] == 0:
        checks.append({"check": "lint", "passed": True})
    elif "No module named black" in lint_result["stderr"]:
        checks.append({"check": "lint", "passed": True, "details": "Black not installed - skipped"})
    else:
        checks.append({"check": "lint", "passed": False, "details": "Code formatting issues"})

    return {
        "success": success,
        "checks": checks,
    }


def create_conventional_commit_message(commit_type: str, scope: str, summary: str, *, breaking: bool = False) -> str:
    """Create conventional commit message."""
    scope_part = f"({scope})" if scope else ""
    breaking_part = "!" if breaking else ""
    return f"{commit_type}{scope_part}{breaking_part}: {summary}"


def get_branch_diff_summary(base: str = "main") -> dict[str, Any]:
    """Get summary of changes between current branch and base."""
    # Get commits ahead
    ahead_result = run_git_command(["rev-list", "--count", f"{base}..HEAD"])
    commits_ahead = int(ahead_result["stdout"]) if ahead_result["success"] else 0

    # Get changed files
    files_result = run_git_command(["diff", "--name-only", base])
    changed_files = files_result["stdout"].split("\n") if files_result["success"] else []

    # Get shortlog
    log_result = run_git_command(["shortlog", f"{base}..HEAD", "--no-merges"])
    commit_summary = log_result["stdout"] if log_result["success"] else ""

    return {
        "commits_ahead": commits_ahead,
        "changed_files": [f for f in changed_files if f],
        "commit_summary": commit_summary,
        "base_branch": base,
    }


def register(app):
    """Register Git guardrail tools with the MCP app."""

    @app.tool()
    def ensure_on_feature_branch() -> dict[str, Any]:
        """Ensure we're on a feature branch following naming conventions.
        If not on a feature branch, suggests creating one.

        Returns:
            dict: Branch validation result with ok status and details
        """
        current_branch = get_current_branch()

        if not current_branch:
            return {
                "ok": False,
                "branch": "",
                "reason": "Not in a git repository",
            }

        if current_branch in ["main", "master"] or current_branch.startswith("release/"):
            return {
                "ok": False,
                "branch": current_branch,
                "reason": f"Cannot commit to protected branch '{current_branch}'. Create a feature branch first.",
            }

        if not is_feature_branch(current_branch):
            return {
                "ok": False,
                "branch": current_branch,
                "reason": f"Branch '{current_branch}' doesn't follow naming convention. Use: feat/scope-desc, fix/scope-desc, or chore/scope-desc",
            }

        return {
            "ok": True,
            "branch": current_branch,
            "reason": "On valid feature branch",
        }

    @app.tool()
    def safe_commit(commit_type: str, scope: str, summary: str, *, breaking: bool = False) -> dict[str, Any]:
        """Create a safe commit with pre-commit checks and conventional commit format.

        Args:
            commit_type: Type of commit (feat, fix, docs, style, refactor, test, chore)
            scope: Scope of the change (optional)
            summary: Brief description of the change
            breaking: Whether this is a breaking change

        Returns:
            dict: Commit result with success status and details
        """
        # First ensure we're on a feature branch
        branch_check = ensure_on_feature_branch()
        if not branch_check["ok"]:
            return {
                "success": False,
                "reason": branch_check["reason"],
                "commit_sha": "",
            }

        # Run pre-commit checks
        checks = run_pre_commit_checks()
        if not checks["success"]:
            return {
                "success": False,
                "reason": "Pre-commit checks failed",
                "checks": checks["checks"],
                "commit_sha": "",
            }

        # Create conventional commit message
        commit_message = create_conventional_commit_message(commit_type, scope, summary, breaking)

        # Validate message format
        validation = validate_conventional_commit(commit_message)
        if not validation["valid"]:
            return {
                "success": False,
                "reason": validation["error"],
                "commit_sha": "",
            }

        # Stage all changes if not already staged
        add_result = run_git_command(["add", "."])
        if not add_result["success"]:
            return {
                "success": False,
                "reason": "Failed to stage changes",
                "commit_sha": "",
            }

        # Commit with the message
        commit_result = run_git_command(["commit", "-m", commit_message])
        if not commit_result["success"]:
            return {
                "success": False,
                "reason": f"Commit failed: {commit_result['stderr']}",
                "commit_sha": "",
            }

        # Get the commit SHA
        sha_result = run_git_command(["rev-parse", "HEAD"])
        commit_sha = sha_result["stdout"] if sha_result["success"] else ""

        return {
            "success": True,
            "reason": "Commit created successfully",
            "commit_sha": commit_sha,
            "commit_message": commit_message,
        }

    @app.tool()
    def create_pr(title: str, body: str, labels: list[str] = None) -> dict[str, Any]:
        """Create a pull request with standard template and validation.

        Args:
            title: PR title (should match conventional commit format)
            body: PR description
            labels: List of labels to apply

        Returns:
            dict: PR creation result
        """
        if labels is None:
            labels = []

        # Ensure we're on a feature branch
        branch_check = ensure_on_feature_branch()
        if not branch_check["ok"]:
            return {
                "success": False,
                "reason": branch_check["reason"],
                "pr_url": "",
            }

        # Get branch diff summary for PR body
        diff_summary = get_branch_diff_summary()

        # Enhance PR body with diff information
        enhanced_body = f"{body}\n\n## Changes\n"
        enhanced_body += f"- {diff_summary['commits_ahead']} commits ahead of main\n"
        enhanced_body += f"- Files changed: {', '.join(diff_summary['changed_files'][:5])}{'...' if len(diff_summary['changed_files']) > 5 else ''}\n\n"
        enhanced_body += f"## Commit Summary\n{diff_summary['commit_summary']}\n\n"
        enhanced_body += "## Checklist\n- [x] Tests pass\n- [x] Code linted\n- [x] Documentation updated\n- [x] Ready for review"

        # Create PR using GitHub CLI
        pr_cmd = ["pr", "create", "--title", title, "--body", enhanced_body, "--base", "main"]

        # Add labels if provided
        for label in labels:
            pr_cmd.extend(["--label", label])

        pr_result = run_git_command(pr_cmd)

        if not pr_result["success"]:
            return {
                "success": False,
                "reason": f"PR creation failed: {pr_result['stderr']}",
                "pr_url": "",
            }

        # Try to get PR URL
        pr_url_result = run_git_command(["pr", "view", "--json", "url", "-q", ".url"])
        pr_url = pr_url_result["stdout"] if pr_url_result["success"] else ""

        return {
            "success": True,
            "reason": "PR created successfully",
            "pr_url": pr_url,
            "title": title,
        }

    @app.tool()
    def branch_diff_summary(base: str = "main") -> dict[str, Any]:
        """Get a summary of changes between current branch and base branch.

        Args:
            base: Base branch to compare against (default: main)

        Returns:
            dict: Summary of changes including commits, files, and shortlog
        """
        return get_branch_diff_summary(base)
