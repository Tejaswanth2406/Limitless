"""FuturistAgent — projects forward trajectories using the TrajectoryEngine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.node import TemporalNode
from ..engine.trajectory_engine import TrajectoryEngine
from .base_agent import AgentResult, BaseAgent


class FuturistAgent(BaseAgent):
    """
    Projects possible futures for each node and selects optimal trajectories.

    The Futurist answers: *What could happen next, and what should we aim for?*
    """

    def __init__(self, horizon: int = 5, branches: int = 3, label: Optional[str] = None):
        super().__init__(label)
        self.engine = TrajectoryEngine(horizon=horizon, branching_factor=branches)

    def run(self, nodes: List[TemporalNode], context: Optional[Dict] = None, **kwargs) -> AgentResult:
        projections: Dict[str, Any] = {}

        for node in nodes:
            label = node.label or node.id[:8]
            trajectories = self.engine.project(node, context=context)
            best = self.engine.select_best(trajectories)

            projections[label] = {
                "trajectories_generated": len(trajectories),
                "best_trajectory": best.label if best else None,
                "best_score": round(best.score(), 4) if best else None,
                "best_terminal_entropy": round(
                    best.terminal_state().entropy, 4
                ) if best and best.terminal_state() else None,
                "best_terminal_omega": round(
                    best.terminal_state().omega(), 4
                ) if best and best.terminal_state() else None,
                "trajectory_scores": [round(t.score(), 4) for t in trajectories],
            }

        findings = {
            "projections": projections,
            "engine_report": self.engine.report(),
        }

        result = AgentResult(
            agent_id=self.id,
            agent_type="Futurist",
            findings=findings,
            confidence=0.75,
            notes=f"Projected futures for {len(nodes)} nodes.",
        )
        return self._record(result)
