#!/usr/bin/env python3
"""Test Code Organization File.

This is a test file in the root directory to verify that the
code-organization.mdc rule auto-attaches properly.

The rule has globs: ["**/*.{py,js,ts,md}"]
This Python file should match the pattern.
"""


def test_code_organization():
    """Test function to verify code organization rules apply."""
    return "This should trigger code-organization.mdc rule"
