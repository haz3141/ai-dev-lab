#!/usr/bin/env python3
"""Test Git Guardrails Validation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "mcp_server/tools"))

from git_guardrails import (
    create_conventional_commit_message,
    get_branch_diff_summary,
    get_current_branch,
    is_feature_branch,
    validate_conventional_commit,
)


def test_current_branch():
    """Test current branch validation."""
    print("=== Testing Current Branch ===")
    current = get_current_branch()
    print(f"Current branch: {current}")
    print(f"Is feature branch: {is_feature_branch(current)}")

    # Simulate ensure_on_feature_branch logic
    if not current:
        print("❌ Not in a git repository")
        return False

    if current in ["main", "master"] or current.startswith("release/"):
        print(f"❌ Cannot commit to protected branch '{current}'. Create a feature branch first.")
        return False

    if not is_feature_branch(current):
        print(f"❌ Branch '{current}' doesn't follow naming convention.")
        print("   Use: feat/scope-desc, fix/scope-desc, or chore/scope-desc")
        return False

    print("✅ On valid feature branch")
    return True

def test_conventional_commits():
    """Test conventional commit validation."""
    print("\n=== Testing Conventional Commits ===")

    test_cases = [
        ("feat: add new feature", True),
        ("fix(ui): resolve button alignment", True),
        ("feat(auth)!: breaking change to login", True),
        ("chore: update dependencies", True),
        ("docs(readme): update installation guide", True),
        ("refactor(utils): simplify helper functions", True),
        ("test: add unit tests", True),
        ("style: format code", True),
        ("invalid message", False),
        ("feat without colon", False),
        ("unknown_type: valid format", False),
    ]

    all_passed = True
    for message, should_be_valid in test_cases:
        result = validate_conventional_commit(message)
        is_valid = result["valid"]

        if is_valid == should_be_valid:
            print(f"✅ '{message}' -> {is_valid}")
        else:
            print(f"❌ '{message}' -> {is_valid} (expected {should_be_valid})")
            if not is_valid:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            all_passed = False

    return all_passed

def test_commit_message_generation():
    """Test commit message generation."""
    print("\n=== Testing Commit Message Generation ===")

    test_cases = [
        ("feat", "docker", "improve signal handling", False),
        ("fix", "auth", "resolve login issue", False),
        ("feat", "api", "add new endpoint", True),
        ("chore", "", "update docs", False),
    ]

    all_valid = True
    for commit_type, scope, summary, breaking in test_cases:
        message = create_conventional_commit_message(commit_type, scope, summary, breaking)
        validation = validate_conventional_commit(message)

        if validation["valid"]:
            print(f"✅ Generated: '{message}'")
        else:
            print(f"❌ Invalid generation: '{message}'")
            print(f"   Error: {validation['error']}")
            all_valid = False

    return all_valid

def test_branch_diff():
    """Test branch diff summary."""
    print("\n=== Testing Branch Diff Summary ===")

    try:
        summary = get_branch_diff_summary("main")
        print(f"✅ Commits ahead: {summary['commits_ahead']}")
        print(f"✅ Changed files: {len(summary['changed_files'])}")
        print(f"✅ Base branch: {summary['base_branch']}")
        if summary["commit_summary"]:
            print("✅ Commit summary available")
        return True
    except Exception as e:
        print(f"❌ Error getting branch diff: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Git Flow Guardrails Validation\n")

    results = []

    # Test current branch (should fail since we're on main)
    results.append(("Current Branch Check", test_current_branch()))

    # Test conventional commit validation
    results.append(("Conventional Commit Validation", test_conventional_commits()))

    # Test commit message generation
    results.append(("Commit Message Generation", test_commit_message_generation()))

    # Test branch diff
    results.append(("Branch Diff Summary", test_branch_diff()))

    print("\n" + "="*50)
    print("📊 VALIDATION RESULTS:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("🎉 All guardrails validation tests PASSED!")
    else:
        print("⚠️  Some guardrails tests FAILED - review above for details")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
