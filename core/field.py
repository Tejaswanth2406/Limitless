"""
TemporalField — the connective fabric between TemporalNodes.

In Limitless, nodes do not communicate via discrete edges alone.
Every node continuously emits influence into a shared field — much like
a mass warps spacetime.  The TemporalField aggregates these influences
and propagates state changes across the network.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from .node import TemporalNode
from .state import TemporalState


class TemporalField:
    """
    A shared dynamic medium through which TemporalNodes interact.

    Responsibilities:
        - Maintain the registry of all nodes.
        - Propagate influence between nodes each tick.
        - Detect resonance (nodes whose temporal signatures align).
        - Identify vortices (unusually stable, high-Ω clusters).
    """

    def __init__(self, decay: float = 0.05):
        """
        Parameters
        ----------
        decay:
            Rate at which influence weakens over temporal distance.
            Higher values = sharper locality.
        """
        self.nodes: Dict[str, TemporalNode] = {}
        self.decay = decay
        self.tick_count = 0
        self.field_log: List[Dict] = []

    # ── Node management ───────────────────────────────────────────────────────

    def register(self, node: TemporalNode) -> None:
        """Add a node to the field."""
        self.nodes[node.id] = node

    def deregister(self, node_id: str) -> None:
        """Remove a node from the field."""
        self.nodes.pop(node_id, None)

    # ── Field propagation ─────────────────────────────────────────────────────

    def tick(self) -> None:
        """
        Advance the field by one time step.

        Each node receives a weighted influence from all other nodes.
        High-Ω (complex, generative) nodes exert more influence.
        Influence falls off with temporal distance.
        """
        self.tick_count += 1
        node_list = list(self.nodes.values())

        for target in node_list:
            total_entropy_pull = 0.0
            total_coherence_pull = 0.0
            total_weight = 0.0

            for source in node_list:
                if source.id == target.id:
                    continue
                influence = source.field_influence(target) * math.exp(-self.decay)
                total_entropy_pull += source.current_state.entropy * influence
                total_coherence_pull += source.current_state.coherence * influence
                total_weight += influence

            if total_weight > 0:
                avg_entropy = total_entropy_pull / total_weight
                avg_coherence = total_coherence_pull / total_weight
                entropy_shift = (avg_entropy - target.current_state.entropy) * 0.05
                target.advance({}, entropy_shift=entropy_shift)

        snapshot = {
            "tick": self.tick_count,
            "avg_entropy": self._avg_entropy(),
            "avg_omega": self._avg_omega(),
        }
        self.field_log.append(snapshot)

    # ── Analysis ──────────────────────────────────────────────────────────────

    def find_resonant_pairs(self, threshold: float = 0.1) -> List[Tuple[str, str, float]]:
        """
        Identify pairs of nodes whose temporal states are closely aligned
        (temporal distance < threshold).  These pairs are in resonance —
        they tend to evolve together.
        """
        pairs = []
        node_list = list(self.nodes.values())
        for i, a in enumerate(node_list):
            for b in node_list[i + 1:]:
                dist = a.temporal_distance(b)
                if dist < threshold:
                    pairs.append((a.label or a.id[:8], b.label or b.id[:8], dist))
        pairs.sort(key=lambda x: x[2])
        return pairs

    def find_vortices(self, omega_threshold: float = 0.3) -> List[TemporalNode]:
        """
        Identify nodes with Ω above threshold — these are 'standing waves'
        in the temporal field: stable, complex, generative structures.
        """
        return [n for n in self.nodes.values() if n.current_state.omega() >= omega_threshold]

    def global_entropy(self) -> float:
        """Mean entropy across all nodes — the field's overall disorder."""
        return self._avg_entropy()

    def global_omega(self) -> float:
        """Mean Ω — the field's overall generative complexity."""
        return self._avg_omega()

    def field_report(self) -> str:
        lines = [
            f"=== TemporalField Report (tick={self.tick_count}) ===",
            f"  Nodes        : {len(self.nodes)}",
            f"  Global Ω     : {self.global_omega():.4f}",
            f"  Global H     : {self.global_entropy():.4f}",
            f"  Vortices     : {len(self.find_vortices())}",
            f"  Resonances   : {len(self.find_resonant_pairs())}",
        ]
        return "\n".join(lines)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _avg_entropy(self) -> float:
        if not self.nodes:
            return 0.0
        return sum(n.current_state.entropy for n in self.nodes.values()) / len(self.nodes)

    def _avg_omega(self) -> float:
        if not self.nodes:
            return 0.0
        return sum(n.current_state.omega() for n in self.nodes.values()) / len(self.nodes)

    def __repr__(self) -> str:
        return f"TemporalField(nodes={len(self.nodes)}, tick={self.tick_count})"
