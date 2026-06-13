"""
Scenario — a reusable, named simulation configuration.

Scenarios define a world's initial entities, their relationships, and a
sequence of pre-scripted events.  They can be replayed, compared, and
forked to explore counterfactuals.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .world import TemporalWorld


@dataclass
class EntitySpec:
    label: str
    initial_state: Dict[str, Any] = field(default_factory=dict)
    entropy: float = 0.5


@dataclass
class LinkSpec:
    label_a: str
    label_b: str
    weight: float = 1.0


@dataclass
class EventSpec:
    target: str
    raw_event: Dict[str, Any]
    at_step: int = 0
    priority: float = 1.0


class Scenario:
    """
    Declarative scenario builder for TemporalWorld simulations.

    Usage
    -----
    >>> s = Scenario("MarketCrash")
    >>> s.add_entity("market",    {"price": 500.0},  entropy=0.3)
    >>> s.add_entity("sentiment", {"score": 0.8},    entropy=0.4)
    >>> s.add_link("market", "sentiment", weight=0.8)
    >>> s.add_event("market", {"type": "text", "raw": "market is crashing"}, at_step=2)
    >>> world = s.build()
    >>> s.run(steps=10)
    >>> s.world.print_summary()
    """

    def __init__(self, name: str = "Scenario"):
        self.name = name
        self._entity_specs: List[EntitySpec] = []
        self._link_specs: List[LinkSpec] = []
        self._event_specs: List[EventSpec] = []
        self.world: Optional[TemporalWorld] = None

    # ── Builder API ───────────────────────────────────────────────────────────

    def add_entity(
        self,
        label: str,
        initial_state: Optional[Dict[str, Any]] = None,
        entropy: float = 0.5,
    ) -> "Scenario":
        self._entity_specs.append(
            EntitySpec(label=label, initial_state=initial_state or {}, entropy=entropy)
        )
        return self

    def add_link(self, label_a: str, label_b: str, weight: float = 1.0) -> "Scenario":
        self._link_specs.append(LinkSpec(label_a=label_a, label_b=label_b, weight=weight))
        return self

    def add_event(
        self,
        target: str,
        raw_event: Dict[str, Any],
        at_step: int = 0,
        priority: float = 1.0,
    ) -> "Scenario":
        self._event_specs.append(
            EventSpec(target=target, raw_event=raw_event, at_step=at_step, priority=priority)
        )
        return self

    # ── Execution ─────────────────────────────────────────────────────────────

    def build(self) -> TemporalWorld:
        """Construct the TemporalWorld from this scenario's spec."""
        self.world = TemporalWorld(self.name)

        for spec in self._entity_specs:
            self.world.add_entity(spec.label, spec.initial_state, spec.entropy)

        for link in self._link_specs:
            self.world.link(link.label_a, link.label_b, link.weight)

        return self.world

    def run(self, steps: int = 10) -> None:
        """Build (if needed) and run for *steps* simulation steps."""
        if self.world is None:
            self.build()

        event_map: Dict[int, List[EventSpec]] = {}
        for ev in self._event_specs:
            event_map.setdefault(ev.at_step, []).append(ev)

        for step in range(steps):
            for ev in event_map.get(step, []):
                self.world.inject_event(ev.target, ev.raw_event, ev.priority)
            self.world.step(1)

    def fork(self, name: Optional[str] = None) -> "Scenario":
        """Create a copy of this scenario with a new name (for counterfactual runs)."""
        new = Scenario(name or f"{self.name}_fork")
        new._entity_specs = copy.deepcopy(self._entity_specs)
        new._link_specs = copy.deepcopy(self._link_specs)
        new._event_specs = copy.deepcopy(self._event_specs)
        return new

    def __repr__(self) -> str:
        return (
            f"Scenario(name={self.name!r}, "
            f"entities={len(self._entity_specs)}, "
            f"events={len(self._event_specs)})"
        )
