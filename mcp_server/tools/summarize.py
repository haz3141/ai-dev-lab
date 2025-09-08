"""Summarize Tool - MCP endpoint for text summarization

Provides text summarization using DSPy or fallback methods.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def summarize_text(text: str, max_length: int = 100) -> dict[str, Any]:
    """Summarize text using available summarization methods.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary

    Returns:
        Dictionary with summary and metadata
    """
    try:
        # Try to use DSPy summarization if available
        from lab.dsp.summarize import Summarize

        summarizer = Summarize()
        summary = summarizer.forward(text)

        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return {
            "summary": summary,
            "method": "dspy",
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0,
        }

    except ImportError as e:
        logger.warning("DSPy not available, using fallback: %s", e)
        return _fallback_summarize(text, max_length)
    except Exception as e:
        logger.error("DSPy summarization failed, using fallback: %s", e)
        return _fallback_summarize(text, max_length)


def _fallback_summarize(text: str, max_length: int) -> dict[str, Any]:
    """Fallback summarization using simple text truncation.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary

    Returns:
        Dictionary with summary and metadata
    """
    if not text:
        return {
            "summary": "",
            "method": "fallback",
            "original_length": 0,
            "summary_length": 0,
            "compression_ratio": 0,
        }

    # Simple fallback: take first sentences up to max_length
    sentences = text.split(". ")
    summary_parts = []
    current_length = 0

    for sentence in sentences:
        if current_length + len(sentence) + 2 <= max_length:  # +2 for ". "
            summary_parts.append(sentence)
            current_length += len(sentence) + 2
        else:
            break

    summary = ". ".join(summary_parts)
    if summary and not summary.endswith("."):
        summary += "."

    return {
        "summary": summary,
        "method": "fallback",
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": len(summary) / len(text) if text else 0,
    }


def get_summarize_health() -> dict[str, Any]:
    """Get health status of the summarize system.

    Returns:
        Health status information
    """
    try:
        # Test if DSPy is available
        from lab.dsp.summarize import Summarize

        summarizer = Summarize()

        # Test with a simple example
        test_result = summarizer.forward("This is a test.")

        return {
            "status": "healthy",
            "method": "dspy",
            "test_successful": True,
            "test_result": test_result,
        }
    except ImportError:
        return {
            "status": "degraded",
            "method": "fallback",
            "test_successful": True,
            "note": "DSPy not available, using fallback method",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "method": "unknown",
            "test_successful": False,
            "error": str(e),
        }
