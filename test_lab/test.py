#!/usr/bin/env python3
"""Test Lab File.

This is a test file in the lab directory to verify that the
lab-development.mdc rule auto-attaches properly.

The rule has globs: ["lab/**/*"]
This file is in test_lab/ which should match the pattern.
"""


class TestLabExperiment:
    """Test class for lab experimentation purposes."""

    def __init__(self):
        self.name = "test_experiment"

    def run_experiment(self):
        """Run a test experiment."""
        return f"Running {self.name} - this should trigger lab-development.mdc rule"
