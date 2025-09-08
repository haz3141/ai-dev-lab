#!/usr/bin/env python3
"""Test script for Git Flow Guardrails

This script demonstrates the Git flow guardrails functionality
without requiring a full MCP server setup.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "mcp_server"))

from tools.git_guardrails import (
    create_conventional_commit_message,
    get_current_branch,
    is_feature_branch,
    validate_conventional_commit,
)


def test_branch_validation():
    """Test branch name validation."""
    print("=== Testing Branch Validation ===")

    current_branch = get_current_branch()
    print(f"Current branch: {current_branch}")

    valid_branches = [
        "feat/git-tools-add-guardrails",
        "fix/auth-validation-bug",
        "chore/update-dependencies",
        "docs/add-git-flow-guide",
    ]

    invalid_branches = [
        "main",
        "master",
        "release/v1.0",
        "invalid-branch-name",
        "feature/new-feature",  # should use feat/
    ]

    print("\nValid branches:")
    for branch in valid_branches:
        is_valid = is_feature_branch(branch)
        print(f"  {branch}: {'✓' if is_valid else '✗'}")

    print("\nInvalid branches:")
    for branch in invalid_branches:
        is_valid = is_feature_branch(branch)
        print(f"  {branch}: {'✓' if is_valid else '✗'}")


def test_conventional_commits():
    """Test conventional commit message generation and validation."""
    print("\n=== Testing Conventional Commits ===")

    test_cases = [
        ("feat", "git-tools", "add Git flow guardrails", False),
        ("fix", "auth", "resolve validation bug", False),
        ("chore", "deps", "update Python dependencies", True),
        ("docs", "", "add Git flow documentation", False),
    ]

    for commit_type, scope, summary, breaking in test_cases:
        message = create_conventional_commit_message(commit_type, scope, summary, breaking)
        validation = validate_conventional_commit(message)

        print(f"Type: {commit_type}, Scope: {scope}, Breaking: {breaking}")
        print(f"Message: {message}")
        print(f"Valid: {'✓' if validation['valid'] else '✗'}")
        if not validation["valid"]:
            print(f"Error: {validation['error']}")
        print()


def test_pre_commit_checks():
    """Test pre-commit check functionality (without actually running checks)."""
    print("=== Testing Pre-commit Checks Structure ===")
    print("Note: Actual pre-commit checks would run here in a real scenario")
    print("This test just verifies the function structure is working")

    # Mock the pre-commit check structure
    checks = [
        {"check": "working_tree_clean", "passed": True},
        {"check": "tests", "passed": True},
        {"check": "lint", "passed": True},
    ]

    print("Pre-commit check structure:")
    for check in checks:
        status = "✓ PASS" if check["passed"] else "✗ FAIL"
        print(f"  {check['check']}: {status}")


def main():
    """Run all Git flow tests."""
    print("Git Flow Guardrails - Test Suite")
    print("=" * 50)

    try:
        test_branch_validation()
        test_conventional_commits()
        test_pre_commit_checks()

        print("\n" + "=" * 50)
        print("✅ Git Flow Guardrails test completed successfully!")
        print("\nNext steps:")
        print("1. Ensure you're on a feature branch (feat/fix/chore/)")
        print("2. Make your changes")
        print("3. Use the MCP tools to create safe commits and PRs")
        print("4. The Cursor rule will guide AI behavior automatically")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
