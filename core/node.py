"""
TemporalNode — a concept or entity modelled as an evolving graph node.

Instead of storing a concept as a static vector, a TemporalNode stores
the concept's *evolution trajectory*: where it came from, what it is now,
and what it might become.  Nodes influence each other like gravitational
or electromagnetic fields — the closer two nodes are in temporal-state
space, the stronger their mutual influence.
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .state import TemporalState


@dataclass
class TemporalNode:
    """A living, evolving entity in the Temporal State Graph."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""

    # Current state
    current_state: TemporalState = field(default_factory=lambda: TemporalState())

    # All past states (full audit trail)
    state_history: List[TemporalState] = field(default_factory=list)

    # Edges: {target_node_id: weight}
    edges: Dict[str, float] = field(default_factory=dict)

    created_at: float = field(default_factory=time.time)

    # ─────────────────────────────────────────────────────────────────────────

    def advance(self, delta: Dict, entropy_shift: float = 0.0) -> TemporalState:
        """Apply a transformation and archive the previous state."""
        self.state_history.append(self.current_state)
        self.current_state = self.current_state.transition(delta, entropy_shift)
        self.current_state.label = self.label
        return self.current_state

    def connect(self, other: "TemporalNode", weight: float = 1.0) -> None:
        """Establish a temporal relationship with another node."""
        self.edges[other.id] = weight
        other.edges[self.id] = weight

    def temporal_distance(self, other: "TemporalNode") -> float:
        """
        Temporal distance between two nodes.

        In this framework 'distance' is not spatial — it is the degree of
        difference between two temporal states.  Nodes with similar entropy
        and coherence profiles are 'close' even if conceptually unrelated.
        """
        s1 = self.current_state
        s2 = other.current_state
        d_entropy = (s1.entropy - s2.entropy) ** 2
        d_coherence = (s1.coherence - s2.coherence) ** 2
        d_momentum = (s1.momentum - s2.momentum) ** 2
        return math.sqrt(d_entropy + d_coherence + d_momentum)

    def field_influence(self, other: "TemporalNode") -> float:
        """
        Influence this node exerts on *other*, modelled as an inverse-square
        law in temporal-distance space (analogous to gravity).
        """
        dist = self.temporal_distance(other)
        if dist < 1e-9:
            return float("inf")
        return self.current_state.omega() / (dist ** 2)

    def age(self) -> float:
        """Seconds since this node was created."""
        return time.time() - self.created_at

    def trajectory_summary(self) -> List[str]:
        """Human-readable snapshot of this node's journey through time."""
        lines = []
        for s in self.state_history[-5:]:
            lines.append(s.summary())
        lines.append(f"→ NOW: {self.current_state.summary()}")
        return lines

    def __repr__(self) -> str:
        return f"TemporalNode(label={self.label!r}, Ω={self.current_state.omega():.4f})"
