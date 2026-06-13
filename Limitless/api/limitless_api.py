"""
Limitless — Top-level API facade.

This is the primary entry point.  Users should import `Limitless` and
interact with the system entirely through this class.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..agents.swarm import AgentSwarm, SwarmReport
from ..core.kernel import TemporalKernel
from ..core.node import TemporalNode
from ..engine.entropy_engine import EntropyEngine
from ..engine.reality_compiler import RealityCompiler
from ..engine.trajectory_engine import TrajectoryEngine
from ..simulation.scenario import Scenario
from ..simulation.world import TemporalWorld
from ..utils.formatters import format_node_table, format_swarm_report


class Limitless:
    """
    Temporal Reality Operating System — top-level API.

    Quick start
    -----------
    >>> lm = Limitless()
    >>> lm.define("market",    {"price": 100.0, "volume": 5000}, entropy=0.35)
    >>> lm.define("sentiment", {"score": 0.7},                    entropy=0.55)
    >>> lm.connect("market", "sentiment")
    >>> lm.observe("market", "text", "The market is declining rapidly and investors are worried")
    >>> lm.tick(5)
    >>> report = lm.think()
    >>> print(lm.render(report))
    """

    def __init__(self, name: str = "Limitless"):
        self.name = name
        self._world = TemporalWorld(name)
        self._swarm = AgentSwarm()

    # ── Entity definition ─────────────────────────────────────────────────────

    def define(
        self,
        label: str,
        state: Optional[Dict[str, Any]] = None,
        entropy: float = 0.5,
    ) -> "Limitless":
        """Define a new entity in the temporal reality."""
        self._world.add_entity(label, initial_state=state or {}, entropy=entropy)
        return self

    def connect(self, label_a: str, label_b: str, weight: float = 1.0) -> "Limitless":
        """Establish a temporal resonance link between two entities."""
        self._world.link(label_a, label_b, weight)
        return self

    # ── Observation ───────────────────────────────────────────────────────────

    def observe(
        self,
        target: str,
        input_type: str,
        raw: Any,
        priority: float = 1.0,
    ) -> "Limitless":
        """
        Inject an observation into a named entity.

        Parameters
        ----------
        target:
            Label of the entity to update.
        input_type:
            'text' | 'numeric' | 'event' | 'signal'
        raw:
            The raw observation data.
        priority:
            Processing priority (higher = processed first).
        """
        self._world.inject_event(target, {"type": input_type, "raw": raw}, priority)
        return self

    # ── Time ─────────────────────────────────────────────────────────────────

    def tick(self, n: int = 1) -> "Limitless":
        """Advance temporal reality by *n* steps."""
        self._world.step(n)
        return self

    # ── Reasoning ─────────────────────────────────────────────────────────────

    def think(self, context: Optional[Dict] = None) -> SwarmReport:
        """
        Run the full multi-agent temporal reasoning swarm.

        Returns a SwarmReport with narrative, risks, and per-agent findings.
        """
        return self._world.analyse(context=context)

    def project(self, label: str, horizon: int = 5) -> str:
        """
        Project the future trajectory of a named entity.

        Returns a human-readable summary of the best trajectory.
        """
        node = self._world.entity(label)
        if node is None:
            return f"Entity '{label}' not found."

        engine = TrajectoryEngine(horizon=horizon, branching_factor=3)
        trajectories = engine.project(node)
        best = engine.select_best(trajectories)

        if best is None:
            return "No trajectories generated."

        lines = [f"Best trajectory for '{label}':", best.summary()]
        for i, step in enumerate(best.steps):
            lines.append(f"  step {i+1}: {step.summary()}")
        return "\n".join(lines)

    # ── Display ───────────────────────────────────────────────────────────────

    def render(self, report: SwarmReport) -> str:
        """Render a SwarmReport as a formatted string."""
        return format_swarm_report(report)

    def table(self) -> str:
        """Display current entities as a formatted table."""
        return format_node_table(self._world.entities())

    def summary(self) -> None:
        """Print a world summary to stdout."""
        self._world.print_summary()

    # ── Scenarios ─────────────────────────────────────────────────────────────

    @staticmethod
    def scenario(name: str = "Scenario") -> Scenario:
        """Create a new Scenario builder."""
        return Scenario(name)

    # ── Introspection ─────────────────────────────────────────────────────────

    def entities(self) -> List[TemporalNode]:
        return self._world.entities()

    def entity(self, label: str) -> Optional[TemporalNode]:
        return self._world.entity(label)

    def snapshot(self) -> Dict[str, Any]:
        return self._world.snapshot()

    @property
    def step_count(self) -> int:
        return self._world._step_count

    def __repr__(self) -> str:
        return (
            f"Limitless(name={self.name!r}, "
            f"entities={len(self.entities())}, "
            f"steps={self.step_count})"
        )
