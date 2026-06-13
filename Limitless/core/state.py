"""
TemporalState — the fundamental unit of Limitless.

Every entity in the framework is not an object with properties,
but a *process* described by its history, current configuration,
entropy signature, and projected future paths.
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TemporalState:
    """
    Represents one instant in the continuous transformation of an entity.

    Rather than storing facts, a TemporalState stores:
        - What the entity IS now (state_vector)
        - How it GOT here (history snapshots)
        - How uncertain / open it is (entropy)
        - What it TENDS toward (momentum)
        - What it COULD become (potential_paths)
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    timestamp: float = field(default_factory=time.time)

    # ── Current configuration ─────────────────────────────────────────────────
    state_vector: Dict[str, Any] = field(default_factory=dict)

    # ── Temporal dynamics ─────────────────────────────────────────────────────
    entropy: float = 0.5          # 0 = fully ordered, 1 = fully chaotic
    coherence: float = 0.5        # 0 = incoherent, 1 = perfectly coherent
    momentum: float = 0.0         # rate of change (signed)
    novelty: float = 0.0          # how different from previous state

    # ── History and projection ────────────────────────────────────────────────
    history: List[Dict[str, Any]] = field(default_factory=list)
    potential_paths: List["TemporalState"] = field(default_factory=list)

    # ── Relational links ──────────────────────────────────────────────────────
    relations: Dict[str, List[str]] = field(default_factory=dict)

    # ── Meta ──────────────────────────────────────────────────────────────────
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ─────────────────────────────────────────────────────────────────────────

    def transition(self, delta: Dict[str, Any], entropy_shift: float = 0.0) -> "TemporalState":
        """
        Produce the *next* TemporalState by applying a transformation delta.

        The current state is archived into history; a fresh state is returned
        with updated vectors and recalculated dynamics.

        Parameters
        ----------
        delta:
            Dictionary of key → new_value changes to apply.
        entropy_shift:
            Signed change to entropy (-= order, += disorder).

        Returns
        -------
        TemporalState
            A new state representing the entity after the transition.
        """
        old_snapshot = {
            "timestamp": self.timestamp,
            "state_vector": dict(self.state_vector),
            "entropy": self.entropy,
            "coherence": self.coherence,
        }

        new_vector = {**self.state_vector, **delta}
        new_entropy = max(0.0, min(1.0, self.entropy + entropy_shift))
        new_coherence = 1.0 - new_entropy
        new_novelty = self._compute_novelty(delta)
        new_momentum = self.momentum * 0.9 + new_novelty * 0.1  # exponential smoothing

        return TemporalState(
            label=self.label,
            timestamp=time.time(),
            state_vector=new_vector,
            entropy=new_entropy,
            coherence=new_coherence,
            momentum=new_momentum,
            novelty=new_novelty,
            history=[*self.history, old_snapshot],
            relations=dict(self.relations),
            metadata=dict(self.metadata),
        )

    def omega(self) -> float:
        """
        Temporal Complexity Score Ω.

        Ω = coherence × entropy × projection_potential

        Higher Ω indicates a rich, complex, highly generative state —
        the kind of state that is interesting for the system to dwell on.
        """
        projection_potential = len(self.potential_paths) / max(1, len(self.potential_paths) + 1)
        return self.coherence * self.entropy * (1.0 + projection_potential)

    def compute_importance(self) -> float:
        """
        Composite importance score used by the Entropy Engine to allocate
        compute resources.  States with high entropy and high momentum are
        more important — they are at critical junctions of possibility.
        """
        return (self.entropy * 0.4) + (abs(self.momentum) * 0.4) + (self.novelty * 0.2)

    def _compute_novelty(self, delta: Dict[str, Any]) -> float:
        """Fraction of keys that actually changed."""
        if not self.state_vector:
            return 1.0
        changed = sum(
            1 for k, v in delta.items()
            if self.state_vector.get(k) != v
        )
        return changed / max(1, len(self.state_vector))

    def summary(self) -> str:
        return (
            f"[{self.label or self.id[:8]}] "
            f"entropy={self.entropy:.2f} coherence={self.coherence:.2f} "
            f"momentum={self.momentum:.3f} Ω={self.omega():.4f}"
        )

    def __repr__(self) -> str:
        return self.summary()
