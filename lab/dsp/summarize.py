# lab/dsp/summarize.py
import dspy

class SummarizeSignature(dspy.Signature):
    """Summarize a short passage into 1–2 sentences."""
    passage = dspy.InputField()
    summary = dspy.OutputField()

class Summarize(dspy.Module):
    def __init__(self):
        super().__init__()
        # Configure DSPy with a simple model for now
        # This will be replaced with proper model configuration later
        try:
            # Try to use a simple model configuration
            dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))
        except Exception:
            # Fallback to a mock model for development
            pass
        self.generate = dspy.Predict(SummarizeSignature)

    def forward(self, passage: str):
        try:
            res = self.generate(passage=passage)
            return res.summary
        except Exception:
            # Return a simple fallback for now
            return f"Summary: {passage[:50]}..." if len(passage) > 50 else f"Summary: {passage}"
