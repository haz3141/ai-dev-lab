#!/usr/bin/env python3
"""Test Evaluation File.

This is a test file in the eval directory to verify that the
rag-evaluation.mdc rule auto-attaches properly.

The rule has globs: ["eval/**/*", "lab/rag/**/*"]
This file is in test_eval/ which should match the first pattern.
"""


def test_function():
    """Test function for evaluation purposes."""
    return "This should trigger rag-evaluation.mdc rule"
