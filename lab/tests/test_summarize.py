import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from lab.dsp.summarize import Summarize


def test_summarize_runs():
    s = Summarize()
    out = s("A short input to summarize.")
    assert isinstance(out, str) and len(out) > 0


if __name__ == "__main__":
    test_summarize_runs()
    print("✓ Test passed!")
