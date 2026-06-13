"""
RealityCompiler — translates raw multi-modal input into temporal state mutations.

All modalities (text, numeric data, structured events) enter the system
through the RealityCompiler.  It produces a unified TemporalState delta
regardless of input type, collapsing the world into a single representation.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from ..core.state import TemporalState


# ── Sentiment heuristics (lightweight, dependency-free) ───────────────────────

_POSITIVE_WORDS = {
    "growth", "increase", "profit", "success", "win", "gain", "rise",
    "stable", "improving", "positive", "high", "strong", "good", "great",
}

_NEGATIVE_WORDS = {
    "loss", "decrease", "fail", "decline", "drop", "risk", "danger",
    "unstable", "deteriorating", "negative", "low", "weak", "bad", "poor",
    "losing", "problem", "issue", "broken", "error",
}


class RealityCompiler:
    """
    Converts raw inputs into temporal state deltas that can be applied to nodes.

    Supported input types:
        - 'text'    : natural language description of a situation
        - 'numeric' : dictionary of measured quantities
        - 'event'   : structured event with type, source, and payload
        - 'signal'  : time-series data point
    """

    def compile(
        self,
        input_type: str,
        raw_input: Any,
        source_label: str = "unknown",
    ) -> Tuple[Dict[str, Any], float]:
        """
        Compile raw input into (delta, entropy_shift).

        Parameters
        ----------
        input_type:
            One of 'text', 'numeric', 'event', 'signal'.
        raw_input:
            The raw data to compile.
        source_label:
            Human-readable label for the input source.

        Returns
        -------
        (delta, entropy_shift)
            delta          : key-value changes to apply to a TemporalState
            entropy_shift  : how much to shift entropy (+disorder / -order)
        """
        if input_type == "text":
            return self._compile_text(raw_input, source_label)
        elif input_type == "numeric":
            return self._compile_numeric(raw_input, source_label)
        elif input_type == "event":
            return self._compile_event(raw_input, source_label)
        elif input_type == "signal":
            return self._compile_signal(raw_input, source_label)
        else:
            return {"__raw__": str(raw_input)}, 0.0

    # ── Text compiler ─────────────────────────────────────────────────────────

    def _compile_text(self, text: str, source: str) -> Tuple[Dict, float]:
        words = set(re.findall(r"\w+", text.lower()))
        pos_hits = len(words & _POSITIVE_WORDS)
        neg_hits = len(words & _NEGATIVE_WORDS)

        sentiment = (pos_hits - neg_hits) / max(1, pos_hits + neg_hits)
        word_count = len(text.split())
        complexity = min(1.0, word_count / 200)   # longer → more complex

        # High complexity + negative sentiment → more entropy
        entropy_shift = complexity * 0.1 - sentiment * 0.05

        delta = {
            "source": source,
            "content_type": "text",
            "word_count": word_count,
            "sentiment": sentiment,
            "complexity": complexity,
            "keywords": list(words & (_POSITIVE_WORDS | _NEGATIVE_WORDS))[:10],
        }
        return delta, entropy_shift

    # ── Numeric compiler ──────────────────────────────────────────────────────

    def _compile_numeric(self, data: Dict[str, float], source: str) -> Tuple[Dict, float]:
        if not data:
            return {"source": source, "content_type": "numeric"}, 0.0

        values = list(data.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)

        # High variance → high entropy shift
        entropy_shift = min(0.2, variance / (abs(mean) + 1e-9) * 0.1)

        delta = {
            "source": source,
            "content_type": "numeric",
            "measurements": data,
            "mean": mean,
            "variance": variance,
        }
        return delta, entropy_shift

    # ── Event compiler ────────────────────────────────────────────────────────

    def _compile_event(self, event: Dict[str, Any], source: str) -> Tuple[Dict, float]:
        event_type = event.get("type", "unknown")
        severity = float(event.get("severity", 0.5))

        # Critical events dramatically increase entropy
        entropy_shift = severity * 0.2

        delta = {
            "source": source,
            "content_type": "event",
            "event_type": event_type,
            "severity": severity,
            "payload": event.get("payload", {}),
        }
        return delta, entropy_shift

    # ── Signal compiler ───────────────────────────────────────────────────────

    def _compile_signal(self, signal: Dict[str, Any], source: str) -> Tuple[Dict, float]:
        """Compile a single time-series data point."""
        value = float(signal.get("value", 0.0))
        prev = float(signal.get("previous", value))
        change = value - prev
        relative_change = change / (abs(prev) + 1e-9)

        entropy_shift = min(0.15, abs(relative_change) * 0.1)

        delta = {
            "source": source,
            "content_type": "signal",
            "value": value,
            "previous": prev,
            "change": change,
            "relative_change": relative_change,
            "signal_name": signal.get("name", "unknown"),
        }
        return delta, entropy_shift

    # ── Batch compile ─────────────────────────────────────────────────────────

    def compile_batch(
        self, inputs: List[Dict[str, Any]]
    ) -> List[Tuple[Dict, float]]:
        """
        Compile multiple inputs at once.

        Each item in `inputs` should have keys:
            type, raw, source (optional)
        """
        results = []
        for item in inputs:
            delta, entropy_shift = self.compile(
                input_type=item.get("type", "text"),
                raw_input=item.get("raw", ""),
                source_label=item.get("source", "batch"),
            )
            results.append((delta, entropy_shift))
        return results
