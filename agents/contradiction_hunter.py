"""
ContradictionHunterAgent — scans temporal states for logical and dynamic contradictions.

A contradiction in the Limitless framework occurs when:
  - A node's entropy and coherence are inconsistent (C ≠ 1 − H).
  - A node's momentum implies it should have already transitioned to a very different state.
  - Two resonant nodes have diverging trajectories (they are close now but moving apart fast).
  - A trajectory projection is internally inconsistent (entropy decreases monotonically when field
    pressure should be increasing it).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from ..core.node import TemporalNode
from .base_agent import AgentResult, BaseAgent


class ContradictionHunterAgent(BaseAgent):
    """
    Detects internal contradictions and inconsistencies across temporal nodes.

    The Contradiction Hunter answers: *Where is the model lying to itself?*
    """

    def __init__(self, tolerance: float = 0.05, label: str = None):
        super().__init__(label)
        self.tolerance = tolerance  # acceptable floating-point slack

    def run(self, nodes: List[TemporalNode], **kwargs) -> AgentResult:
        contradictions: List[Dict[str, Any]] = []

        for node in nodes:
            contradictions.extend(self._check_coherence_entropy(node))
            contradictions.extend(self._check_momentum_state(node))
            contradictions.extend(self._check_trajectory_consistency(node))

        pair_contradictions = self._check_resonance_divergence(nodes)
        contradictions.extend(pair_contradictions)

        severity = self._aggregate_severity(contradictions)

        findings = {
            "contradiction_count": len(contradictions),
            "contradictions": contradictions,
            "severity": round(severity, 4),
            "clean": len(contradictions) == 0,
        }

        confidence = max(0.0, 1.0 - severity)
        result = AgentResult(
            agent_id=self.id,
            agent_type="ContradictionHunter",
            findings=findings,
            confidence=confidence,
            notes=f"Found {len(contradictions)} contradiction(s). Severity={severity:.3f}",
        )
        return self._record(result)

    # ── Contradiction checks ──────────────────────────────────────────────────

    def _check_coherence_entropy(self, node: TemporalNode) -> List[Dict]:
        """C + H must equal 1.0 within tolerance."""
        s = node.current_state
        delta = abs((s.coherence + s.entropy) - 1.0)
        if delta > self.tolerance:
            return [{
                "node": node.label or node.id[:8],
                "type": "coherence_entropy_mismatch",
                "detail": f"H={s.entropy:.4f} + C={s.coherence:.4f} = {s.entropy+s.coherence:.4f} ≠ 1.0",
                "severity": min(1.0, delta * 5),
            }]
        return []

    def _check_momentum_state(self, node: TemporalNode) -> List[Dict]:
        """High momentum with no history suggests an ungrounded state change."""
        s = node.current_state
        if abs(s.momentum) > 0.6 and not node.state_history:
            return [{
                "node": node.label or node.id[:8],
                "type": "ungrounded_momentum",
                "detail": f"momentum={s.momentum:.4f} but no history to justify it",
                "severity": min(1.0, abs(s.momentum)),
            }]
        return []

    def _check_trajectory_consistency(self, node: TemporalNode) -> List[Dict]:
        """Entropy should not systematically decrease when momentum is positive."""
        issues = []
        history = node.state_history
        if len(history) < 3:
            return []
        recent = history[-3:]
        entropies = [s.entropy for s in recent] + [node.current_state.entropy]
        # If momentum > 0 (entropy increasing) but entropy is actually falling 3 steps in a row
        avg_momentum = sum(s.momentum for s in recent) / len(recent)
        if avg_momentum > 0.1:
            if all(entropies[i] > entropies[i+1] for i in range(len(entropies)-1)):
                issues.append({
                    "node": node.label or node.id[:8],
                    "type": "momentum_entropy_contradiction",
                    "detail": f"positive momentum ({avg_momentum:.3f}) but entropy falling monotonically",
                    "severity": 0.5,
                })
        return issues

    def _check_resonance_divergence(self, nodes: List[TemporalNode]) -> List[Dict]:
        """
        Resonant pairs (temporally close) that have opposite momentums are
        about to violently diverge — a structural instability.
        """
        issues = []
        for i, a in enumerate(nodes):
            for b in nodes[i+1:]:
                dist = a.temporal_distance(b)
                if dist < 0.1:  # resonant
                    momentum_product = a.current_state.momentum * b.current_state.momentum
                    if momentum_product < -0.1:  # opposite signs
                        issues.append({
                            "nodes": [a.label or a.id[:8], b.label or b.id[:8]],
                            "type": "resonant_divergence",
                            "detail": (
                                f"nodes are resonant (d={dist:.3f}) but have opposing momentums "
                                f"({a.current_state.momentum:.3f}, {b.current_state.momentum:.3f})"
                            ),
                            "severity": min(1.0, abs(momentum_product) * 2),
                        })
        return issues

    def _aggregate_severity(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        return min(1.0, sum(c.get("severity", 0.5) for c in contradictions) / max(1, len(contradictions)))
