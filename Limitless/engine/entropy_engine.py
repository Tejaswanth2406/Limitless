"""
EntropyEngine — measures, tracks, and uses entropy to drive compute allocation.

In Limitless, entropy is not merely a measure of disorder.  Entropy is the
universe's way of expanding possibility.  High-entropy states are at critical
junctions — they have the most potential to branch into new configurations.
The EntropyEngine therefore allocates more reasoning compute to high-entropy
nodes, and less to stable, low-entropy nodes.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from ..core.node import TemporalNode
from ..core.state import TemporalState


class EntropyEngine:
    """
    Entropy-driven analysis and compute scheduling for the Limitless system.

    Key concepts:
        - Entropy Score    : how disordered / open a node's current state is.
        - Novelty Score    : how different the latest transition was.
        - Importance Score : composite, drives resource allocation.
        - Expansion Rate   : how fast a node's possibility space is growing.
    """

    # ── Per-node metrics ──────────────────────────────────────────────────────

    def score(self, node: TemporalNode) -> Dict[str, float]:
        """
        Full entropy analysis for a single node.

        Returns
        -------
        dict with keys:
            entropy, coherence, novelty, momentum, omega, importance,
            expansion_rate, stability_index
        """
        s = node.current_state
        expansion_rate = self._expansion_rate(node)
        stability_index = self._stability_index(node)

        return {
            "entropy": s.entropy,
            "coherence": s.coherence,
            "novelty": s.novelty,
            "momentum": s.momentum,
            "omega": s.omega(),
            "importance": s.compute_importance(),
            "expansion_rate": expansion_rate,
            "stability_index": stability_index,
        }

    def rank_nodes(self, nodes: List[TemporalNode]) -> List[Tuple[TemporalNode, float]]:
        """
        Rank nodes by importance (descending).
        High importance → allocate more compute.
        """
        ranked = [(n, n.current_state.compute_importance()) for n in nodes]
        ranked.sort(key=lambda x: -x[1])
        return ranked

    def allocate_compute(
        self, nodes: List[TemporalNode], total_budget: float = 1.0
    ) -> Dict[str, float]:
        """
        Distribute a compute budget across nodes proportional to importance.

        Parameters
        ----------
        nodes:
            List of TemporalNodes to consider.
        total_budget:
            Total compute units to distribute (arbitrary scale).

        Returns
        -------
        dict: {node_id → allocated_compute}
        """
        if not nodes:
            return {}

        scores = {n.id: n.current_state.compute_importance() for n in nodes}
        total = sum(scores.values()) or 1.0

        return {nid: (imp / total) * total_budget for nid, imp in scores.items()}

    # ── Global field metrics ──────────────────────────────────────────────────

    def field_entropy_gradient(self, nodes: List[TemporalNode]) -> float:
        """
        Variance in entropy across all nodes.
        A high gradient means some areas of the field are ordered while
        others are chaotic — interesting structure is forming.
        """
        if len(nodes) < 2:
            return 0.0
        entropies = [n.current_state.entropy for n in nodes]
        mean = sum(entropies) / len(entropies)
        variance = sum((e - mean) ** 2 for e in entropies) / len(entropies)
        return math.sqrt(variance)

    def detect_phase_transition(
        self, nodes: List[TemporalNode], threshold: float = 0.3
    ) -> List[TemporalNode]:
        """
        Identify nodes undergoing rapid entropy change — phase transitions.

        A phase transition is when a state crosses from ordered to chaotic
        (or vice versa) — the most informationally rich moment in a node's life.
        """
        transitioning = []
        for node in nodes:
            if len(node.state_history) < 2:
                continue
            prev_entropy = node.state_history[-1].entropy
            curr_entropy = node.current_state.entropy
            if abs(curr_entropy - prev_entropy) >= threshold:
                transitioning.append(node)
        return transitioning

    def total_possibility_space(self, nodes: List[TemporalNode]) -> float:
        """
        Estimate the total reachable state count across all nodes.
        This is a proxy for the universe's current 'openness'.
        """
        return sum(
            2 ** (n.current_state.entropy * 10)  # entropy → bit-count → states
            for n in nodes
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _expansion_rate(self, node: TemporalNode) -> float:
        """How fast the node's entropy has been increasing."""
        if len(node.state_history) < 2:
            return 0.0
        prev = node.state_history[-1].entropy
        return node.current_state.entropy - prev

    def _stability_index(self, node: TemporalNode) -> float:
        """
        1.0 = perfectly stable (no change over last N steps).
        0.0 = maximally volatile.
        """
        history = node.state_history[-5:]
        if not history:
            return 1.0
        entropies = [s.entropy for s in history]
        if not entropies:
            return 1.0
        variance = sum(
            (e - (sum(entropies) / len(entropies))) ** 2 for e in entropies
        ) / len(entropies)
        return max(0.0, 1.0 - (variance * 10))

    def report(self, nodes: List[TemporalNode]) -> str:
        lines = [
            "=== EntropyEngine Report ===",
            f"  Nodes analysed     : {len(nodes)}",
            f"  Entropy gradient   : {self.field_entropy_gradient(nodes):.4f}",
            f"  Phase transitions  : {len(self.detect_phase_transition(nodes))}",
            f"  Possibility space  : {self.total_possibility_space(nodes):.2e}",
        ]
        ranked = self.rank_nodes(nodes)
        lines.append("  Top nodes by importance:")
        for node, imp in ranked[:5]:
            lines.append(f"    {node.label or node.id[:8]:<20} importance={imp:.4f}")
        return "\n".join(lines)
