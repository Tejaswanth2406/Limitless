"""
TemporalKernel — the central scheduler and reality compiler of Limitless.

The kernel sits beneath everything.  Its responsibilities mirror those of
an OS kernel, but instead of managing CPU / memory / I/O, it manages:

    - State transitions (process scheduling analogue)
    - Entropy budgets    (memory allocation analogue)
    - Temporal routing   (I/O scheduling analogue)
    - Reality snapshots  (file-system analogue)

Input enters the kernel not as text, but as raw events.  The kernel
translates events into TemporalState mutations and dispatches them through
the TemporalField.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .field import TemporalField
from .node import TemporalNode
from .state import TemporalState


@dataclass
class KernelEvent:
    """A discrete input to the kernel."""
    source: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: float = 1.0   # 0 = low, 1 = normal, 10 = critical


class TemporalKernel:
    """
    Temporal Reality Kernel.

    The kernel maintains the TemporalField and provides:
        - Event ingestion and translation into state mutations.
        - Entropy-driven compute allocation (high-importance states processed first).
        - Plugin / middleware hooks for custom processing pipelines.
        - Reality snapshots (immutable records of the field at a given tick).
    """

    def __init__(self):
        self.field = TemporalField()
        self._event_queue: List[KernelEvent] = []
        self._middlewares: List[Callable] = []
        self._snapshots: List[Dict] = []
        self.uptime_start = time.time()

    # ── Node management ───────────────────────────────────────────────────────

    def spawn_node(self, label: str, initial_state: Optional[Dict] = None,
                   entropy: float = 0.5) -> TemporalNode:
        """Create a new TemporalNode and register it in the field."""
        state = TemporalState(
            label=label,
            state_vector=initial_state or {},
            entropy=entropy,
            coherence=1.0 - entropy,
        )
        node = TemporalNode(label=label, current_state=state)
        self.field.register(node)
        return node

    def link_nodes(self, a: TemporalNode, b: TemporalNode, weight: float = 1.0) -> None:
        """Establish a temporal resonance link between two nodes."""
        a.connect(b, weight)

    # ── Event pipeline ────────────────────────────────────────────────────────

    def ingest(self, source: str, payload: Dict[str, Any], priority: float = 1.0) -> None:
        """
        Accept a raw event and enqueue it for processing.

        The kernel converts events into state mutations; callers should not
        manipulate nodes directly — route all changes through ingest().
        """
        event = KernelEvent(source=source, payload=payload, priority=priority)
        self._event_queue.append(event)
        self._event_queue.sort(key=lambda e: -e.priority)   # highest priority first

    def add_middleware(self, fn: Callable[[KernelEvent], Optional[KernelEvent]]) -> None:
        """
        Register a middleware function.

        Middlewares run in order for each event.  A middleware may:
            - Return the event (possibly modified) to continue processing.
            - Return None to drop the event.
        """
        self._middlewares.append(fn)

    def process_events(self) -> int:
        """
        Drain the event queue.

        Returns
        -------
        int
            Number of events successfully processed.
        """
        processed = 0
        while self._event_queue:
            event = self._event_queue.pop(0)

            # Run through middlewares
            for mw in self._middlewares:
                event = mw(event)
                if event is None:
                    break

            if event is None:
                continue

            # Dispatch: find the node matching the event source
            target = self._find_node(event.source)
            if target:
                # Entropy shift: critical events increase disorder
                entropy_shift = 0.05 * (event.priority / 10.0)
                target.advance(event.payload, entropy_shift=entropy_shift)
            processed += 1

        return processed

    # ── Tick ─────────────────────────────────────────────────────────────────

    def tick(self, process: bool = True) -> None:
        """
        Advance the kernel by one step:
            1. Process all queued events.
            2. Propagate influences through the field.
        """
        if process:
            self.process_events()
        self.field.tick()

    # ── Snapshots ─────────────────────────────────────────────────────────────

    def snapshot(self) -> Dict:
        """Capture an immutable record of the current field state."""
        snap = {
            "tick": self.field.tick_count,
            "timestamp": time.time(),
            "uptime": time.time() - self.uptime_start,
            "global_entropy": self.field.global_entropy(),
            "global_omega": self.field.global_omega(),
            "node_count": len(self.field.nodes),
            "nodes": {
                nid: {
                    "label": n.label,
                    "entropy": n.current_state.entropy,
                    "coherence": n.current_state.coherence,
                    "omega": n.current_state.omega(),
                    "momentum": n.current_state.momentum,
                }
                for nid, n in self.field.nodes.items()
            },
        }
        self._snapshots.append(snap)
        return snap

    def replay(self, from_tick: int = 0) -> List[Dict]:
        """Return all snapshots from a given tick onward."""
        return [s for s in self._snapshots if s["tick"] >= from_tick]

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> str:
        return (
            f"TemporalKernel | uptime={time.time()-self.uptime_start:.1f}s | "
            + self.field.field_report()
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _find_node(self, label_or_id: str) -> Optional[TemporalNode]:
        for node in self.field.nodes.values():
            if node.label == label_or_id or node.id == label_or_id:
                return node
        return None

    def __repr__(self) -> str:
        return f"TemporalKernel(nodes={len(self.field.nodes)}, ticks={self.field.tick_count})"
