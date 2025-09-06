# lab/dsp/summarize.py
import dspy

class SummarizeSignature(dspy.Signature):
    """Summarize a short passage into 1–2 sentences."""
    passage = dspy.InputField()
    summary = dspy.OutputField()

class Summarize(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(SummarizeSignature)

    def forward(self, passage: str):
        res = self.generate(passage=passage)
        return res.summary
