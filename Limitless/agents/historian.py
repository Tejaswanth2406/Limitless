"""HistorianAgent — reconstructs the temporal trajectory of each node."""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.node import TemporalNode
from .base_agent import AgentResult, BaseAgent


class HistorianAgent(BaseAgent):
    """
    Analyses state history to identify patterns, trends, and turning points.

    The Historian answers: *How did we get here?*
    """

    def run(self, nodes: List[TemporalNode], **kwargs) -> AgentResult:
        histories: Dict[str, Any] = {}

        for node in nodes:
            history = node.state_history
            label = node.label or node.id[:8]

            if not history:
                histories[label] = {"status": "no_history"}
                continue

            entropy_series = [s.entropy for s in history]
            coherence_series = [s.coherence for s in history]

            # Trend: positive = increasing, negative = decreasing
            entropy_trend = self._trend(entropy_series)
            coherence_trend = self._trend(coherence_series)

            # Turning points: where entropy changed direction
            turning_points = self._turning_points(entropy_series)

            histories[label] = {
                "depth": len(history),
                "entropy_trend": round(entropy_trend, 4),
                "coherence_trend": round(coherence_trend, 4),
                "turning_points": turning_points,
                "initial_entropy": round(entropy_series[0], 4),
                "current_entropy": round(node.current_state.entropy, 4),
                "net_entropy_change": round(
                    node.current_state.entropy - entropy_series[0], 4
                ),
            }

        findings = {
            "histories": histories,
            "total_nodes_with_history": sum(
                1 for v in histories.values() if v.get("depth", 0) > 0
            ),
        }

        result = AgentResult(
            agent_id=self.id,
            agent_type="Historian",
            findings=findings,
            confidence=0.9,
            notes="History reconstruction complete.",
        )
        return self._record(result)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _trend(self, series: List[float]) -> float:
        """Simple linear regression slope."""
        n = len(series)
        if n < 2:
            return 0.0
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(series) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series))
        den = sum((x - mean_x) ** 2 for x in xs)
        return num / den if den else 0.0

    def _turning_points(self, series: List[float]) -> List[int]:
        """Indices where the series changes direction."""
        points = []
        for i in range(1, len(series) - 1):
            if (series[i] > series[i - 1] and series[i] > series[i + 1]) or \
               (series[i] < series[i - 1] and series[i] < series[i + 1]):
                points.append(i)
        return points
