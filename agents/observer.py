"""ObserverAgent — extracts present-state facts from a set of TemporalNodes."""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.node import TemporalNode
from .base_agent import AgentResult, BaseAgent


class ObserverAgent(BaseAgent):
    """
    Observes the current field state and catalogues facts.

    The Observer does not reason about the past or future.
    It answers: *What is true right now?*
    """

    def run(self, nodes: List[TemporalNode], **kwargs) -> AgentResult:
        observations: Dict[str, Any] = {}

        for node in nodes:
            s = node.current_state
            observations[node.label or node.id[:8]] = {
                "entropy": round(s.entropy, 4),
                "coherence": round(s.coherence, 4),
                "omega": round(s.omega(), 4),
                "momentum": round(s.momentum, 4),
                "novelty": round(s.novelty, 4),
                "state_keys": list(s.state_vector.keys()),
                "history_depth": len(node.state_history),
            }

        # Global field stats
        entropies = [n.current_state.entropy for n in nodes]
        avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0
        max_entropy_node = max(nodes, key=lambda n: n.current_state.entropy, default=None)
        min_entropy_node = min(nodes, key=lambda n: n.current_state.entropy, default=None)

        findings = {
            "observations": observations,
            "node_count": len(nodes),
            "avg_entropy": round(avg_entropy, 4),
            "most_chaotic": max_entropy_node.label if max_entropy_node else None,
            "most_ordered": min_entropy_node.label if min_entropy_node else None,
        }

        confidence = 1.0 if nodes else 0.0
        result = AgentResult(
            agent_id=self.id,
            agent_type="Observer",
            findings=findings,
            confidence=confidence,
            notes=f"Observed {len(nodes)} nodes.",
        )
        return self._record(result)
