"""
TemporalWorld — a self-contained simulated reality built on Limitless primitives.

A world is a collection of named entities (TemporalNodes) evolving inside a
TemporalKernel.  Users can inject events, advance time, and observe how the
world's state changes over simulated steps.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from ..core.kernel import TemporalKernel
from ..core.node import TemporalNode
from ..engine.entropy_engine import EntropyEngine
from ..engine.reality_compiler import RealityCompiler
from ..agents.swarm import AgentSwarm, SwarmReport


class TemporalWorld:
    """
    A simulated temporal reality.

    Usage
    -----
    >>> world = TemporalWorld("EconomyWorld")
    >>> world.add_entity("market",     initial_state={"price": 100.0}, entropy=0.4)
    >>> world.add_entity("sentiment",  initial_state={"score": 0.6},   entropy=0.6)
    >>> world.inject_event("market",   {"type": "text", "raw": "market is losing ground"})
    >>> world.step(n=5)
    >>> report = world.analyse()
    >>> world.print_summary()
    """

    def __init__(self, name: str = "World"):
        self.name = name
        self.kernel = TemporalKernel()
        self.compiler = RealityCompiler()
        self.entropy_engine = EntropyEngine()
        self.swarm = AgentSwarm()
        self._entities: Dict[str, TemporalNode] = {}
        self._step_count = 0
        self.created_at = time.time()

    # ── Entity management ─────────────────────────────────────────────────────

    def add_entity(
        self,
        label: str,
        initial_state: Optional[Dict[str, Any]] = None,
        entropy: float = 0.5,
    ) -> TemporalNode:
        """Add a named entity to the world."""
        node = self.kernel.spawn_node(label, initial_state=initial_state, entropy=entropy)
        self._entities[label] = node
        return node

    def link(self, label_a: str, label_b: str, weight: float = 1.0) -> None:
        """Create a temporal resonance link between two entities."""
        a = self._entities.get(label_a)
        b = self._entities.get(label_b)
        if a and b:
            self.kernel.link_nodes(a, b, weight)

    # ── Event injection ───────────────────────────────────────────────────────

    def inject_event(
        self,
        target_label: str,
        raw_event: Dict[str, Any],
        priority: float = 1.0,
    ) -> None:
        """
        Compile a raw event and inject it into the kernel's event queue.

        raw_event should have keys: 'type' ('text'|'numeric'|'event'|'signal')
        and 'raw' (the payload).
        """
        delta, entropy_shift = self.compiler.compile(
            input_type=raw_event.get("type", "text"),
            raw_input=raw_event.get("raw", raw_event),
            source_label=target_label,
        )
        # Fold entropy_shift into the payload so the kernel can use it
        payload = {**delta, "__entropy_shift__": entropy_shift}
        self.kernel.ingest(target_label, payload, priority=priority)

    # ── Time advancement ──────────────────────────────────────────────────────

    def step(self, n: int = 1) -> None:
        """Advance the world by *n* simulation steps."""
        for _ in range(n):
            self.kernel.tick()
            self._step_count += 1

    # ── Analysis ──────────────────────────────────────────────────────────────

    def analyse(self, context: Optional[Dict] = None) -> SwarmReport:
        """Run the full agent swarm on the current world state."""
        nodes = list(self._entities.values())
        return self.swarm.run(nodes, context=context, run_id=f"step-{self._step_count}")

    def snapshot(self) -> Dict[str, Any]:
        """Capture the current world state as a dictionary."""
        return self.kernel.snapshot()

    # ── Display ───────────────────────────────────────────────────────────────

    def print_summary(self) -> None:
        nodes = list(self._entities.values())
        print(f"\n{'='*60}")
        print(f"  {self.name}  (step={self._step_count})")
        print(f"{'='*60}")
        for node in nodes:
            s = node.current_state
            bar_h = "█" * int(s.entropy * 20)
            bar_c = "░" * int(s.coherence * 20)
            print(
                f"  {node.label:<18} "
                f"H={s.entropy:.2f} [{bar_h:<20}] "
                f"Ω={s.omega():.3f}"
            )
        print(f"{'='*60}")
        print(self.entropy_engine.report(nodes))
        print(f"{'='*60}\n")

    def entity(self, label: str) -> Optional[TemporalNode]:
        return self._entities.get(label)

    def entities(self) -> List[TemporalNode]:
        return list(self._entities.values())

    def __repr__(self) -> str:
        return (
            f"TemporalWorld(name={self.name!r}, "
            f"entities={len(self._entities)}, "
            f"steps={self._step_count})"
        )
