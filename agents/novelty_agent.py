"""
NoveltyAgent — identifies genuinely new configurations that have no precedent in history.

In the Limitless framework, novelty is not a bug — it is the mechanism through which
the universe expands its possibility space.  The NoveltyAgent celebrates novelty and
flags nodes that are exploring genuinely unprecedented territory.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from ..core.node import TemporalNode
from ..core.state import TemporalState
from .base_agent import AgentResult, BaseAgent


class NoveltyAgent(BaseAgent):
    """
    Measures and celebrates novelty — states that have no historical precedent.

    The Novelty Agent answers: *What is genuinely new here?*
    """

    def __init__(self, novelty_threshold: float = 0.4, label: Optional[str] = None):
        super().__init__(label)
        self.novelty_threshold = novelty_threshold

    def run(self, nodes: List[TemporalNode], **kwargs) -> AgentResult:
        novel_nodes: List[Dict[str, Any]] = []
        scores: Dict[str, float] = {}

        for node in nodes:
            score = self._novelty_score(node)
            scores[node.label or node.id[:8]] = round(score, 4)
            if score >= self.novelty_threshold:
                novel_nodes.append({
                    "node": node.label or node.id[:8],
                    "novelty_score": round(score, 4),
                    "current_entropy": round(node.current_state.entropy, 4),
                    "reason": self._novelty_reason(node, score),
                })

        novel_nodes.sort(key=lambda x: -x["novelty_score"])

        global_novelty = sum(scores.values()) / max(1, len(scores))

        findings = {
            "novel_nodes": novel_nodes,
            "novelty_scores": scores,
            "global_novelty": round(global_novelty, 4),
            "threshold": self.novelty_threshold,
            "frontier_count": len(novel_nodes),
        }

        result = AgentResult(
            agent_id=self.id,
            agent_type="NoveltyAgent",
            findings=findings,
            confidence=0.85,
            notes=f"{len(novel_nodes)} node(s) on the novelty frontier.",
        )
        return self._record(result)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _novelty_score(self, node: TemporalNode) -> float:
        """
        Composite novelty score based on:
          - Raw novelty from TSV (ν)
          - Distance from historical mean state
          - Entropy momentum (rising entropy = exploring new territory)
        """
        s = node.current_state
        raw_novelty = s.novelty                          # 0–1 from state delta

        # Distance from historical mean entropy
        hist_entropies = [h.entropy for h in node.state_history]
        if hist_entropies:
            mean_h = sum(hist_entropies) / len(hist_entropies)
            hist_distance = abs(s.entropy - mean_h)
        else:
            hist_distance = 0.0

        # Positive momentum = moving away from known territory
        momentum_bonus = max(0.0, s.momentum) * 0.2

        return min(1.0, raw_novelty * 0.5 + hist_distance * 0.3 + momentum_bonus)

    def _novelty_reason(self, node: TemporalNode, score: float) -> str:
        s = node.current_state
        if s.novelty > 0.7:
            return "large state-vector change from previous step"
        if s.momentum > 0.3:
            return "high positive entropic momentum — rapidly expanding possibility space"
        if not node.state_history:
            return "no historical baseline — first observation"
        hist_h = sum(h.entropy for h in node.state_history) / len(node.state_history)
        if abs(s.entropy - hist_h) > 0.2:
            return f"entropy ({s.entropy:.2f}) diverged significantly from historical mean ({hist_h:.2f})"
        return "composite novelty above threshold"
