"""
TrajectoryEngine — projects possible future states from the current temporal state.

Instead of predicting the next token, the TrajectoryEngine predicts the next
*state* — branching into multiple possible futures, scoring each by probability,
coherence, entropy cost, and utility.
"""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.node import TemporalNode
from ..core.state import TemporalState


@dataclass
class Trajectory:
    """A single possible future path from a source state."""
    steps: List[TemporalState]
    probability: float = 1.0
    coherence: float = 1.0
    utility: float = 0.0
    entropy_cost: float = 0.0
    label: str = ""

    def terminal_state(self) -> Optional[TemporalState]:
        return self.steps[-1] if self.steps else None

    def score(self) -> float:
        """Composite desirability score."""
        return (self.probability * 0.3) + (self.coherence * 0.3) + \
               (self.utility * 0.3) - (self.entropy_cost * 0.1)

    def summary(self) -> str:
        return (
            f"Trajectory '{self.label}': steps={len(self.steps)} "
            f"P={self.probability:.2f} coherence={self.coherence:.2f} "
            f"utility={self.utility:.2f} score={self.score():.4f}"
        )


class TrajectoryEngine:
    """
    Generates, evaluates, and selects optimal future trajectories.

    Rather than asking 'what word comes next?', the engine asks:
        'What future configurations of reality become reachable?'
    """

    def __init__(self, horizon: int = 5, branching_factor: int = 3):
        """
        Parameters
        ----------
        horizon:
            Number of future steps to simulate per trajectory.
        branching_factor:
            Number of alternative branches at each step.
        """
        self.horizon = horizon
        self.branching_factor = branching_factor
        self._trajectory_history: List[Trajectory] = []

    def project(
        self,
        node: TemporalNode,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Trajectory]:
        """
        Generate `branching_factor` candidate trajectories for *node*.

        Each trajectory is a plausible future sequence of TemporalStates,
        produced by applying different hypothetical transformation deltas.

        Parameters
        ----------
        node:
            The node whose future we are projecting.
        context:
            Optional external context that biases trajectory generation.

        Returns
        -------
        List[Trajectory] sorted by composite score (best first).
        """
        trajectories: List[Trajectory] = []
        base_state = node.current_state

        for b in range(self.branching_factor):
            steps: List[TemporalState] = []
            current = base_state

            for h in range(self.horizon):
                delta = self._hypothetical_delta(current, branch_index=b, step=h, context=context)
                entropy_shift = self._entropy_shift(current, branch_index=b)
                current = current.transition(delta, entropy_shift)
                steps.append(current)

            traj = Trajectory(
                steps=steps,
                probability=self._estimate_probability(steps, base_state),
                coherence=self._estimate_coherence(steps),
                utility=self._estimate_utility(steps, context),
                entropy_cost=sum(max(0, s.entropy - base_state.entropy) for s in steps),
                label=f"branch-{b}",
            )
            trajectories.append(traj)

        trajectories.sort(key=lambda t: -t.score())
        self._trajectory_history.extend(trajectories)
        return trajectories

    def select_best(self, trajectories: List[Trajectory]) -> Optional[Trajectory]:
        """Return the highest-scoring trajectory."""
        return trajectories[0] if trajectories else None

    def simulate_convergence(
        self,
        nodes: List[TemporalNode],
        steps: int = 10,
    ) -> Dict[str, List[float]]:
        """
        Run a multi-step simulation across multiple nodes and record how
        their Ω (temporal complexity) evolves.  Used to identify which
        nodes converge to stability and which remain volatile.
        """
        history: Dict[str, List[float]] = {n.id: [] for n in nodes}

        for _ in range(steps):
            for node in nodes:
                node.advance({}, entropy_shift=random.uniform(-0.02, 0.02))
                history[node.id].append(node.current_state.omega())

        return history

    def compare_trajectories(self, t1: Trajectory, t2: Trajectory) -> Dict[str, float]:
        """Side-by-side comparison of two trajectories."""
        return {
            "score_diff": t1.score() - t2.score(),
            "probability_diff": t1.probability - t2.probability,
            "coherence_diff": t1.coherence - t2.coherence,
            "utility_diff": t1.utility - t2.utility,
            "entropy_cost_diff": t1.entropy_cost - t2.entropy_cost,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _hypothetical_delta(
        self,
        state: TemporalState,
        branch_index: int,
        step: int,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate a plausible state mutation for a hypothetical future step.

        Real implementation would consult learned transition models;
        here we produce deterministic-ish variations keyed on branch/step.
        """
        seed_val = (branch_index + 1) * (step + 1)
        perturbation = math.sin(seed_val) * 0.1

        delta: Dict[str, Any] = {"__step__": step, "__branch__": branch_index}
        if context:
            delta.update({f"ctx_{k}": v for k, v in list(context.items())[:3]})

        for key in list(state.state_vector.keys())[:3]:
            val = state.state_vector[key]
            if isinstance(val, (int, float)):
                delta[key] = val + perturbation

        return delta

    def _entropy_shift(self, state: TemporalState, branch_index: int) -> float:
        """Branches with higher index explore more chaotic futures."""
        base = 0.01 * branch_index
        return base * (1.0 - state.coherence)

    def _estimate_probability(
        self, steps: List[TemporalState], base: TemporalState
    ) -> float:
        """Higher coherence and lower entropy change → more probable."""
        if not steps:
            return 0.0
        avg_coherence = sum(s.coherence for s in steps) / len(steps)
        entropy_drift = abs(steps[-1].entropy - base.entropy)
        return max(0.0, avg_coherence * math.exp(-entropy_drift * 2))

    def _estimate_coherence(self, steps: List[TemporalState]) -> float:
        if not steps:
            return 0.0
        return sum(s.coherence for s in steps) / len(steps)

    def _estimate_utility(
        self, steps: List[TemporalState], context: Optional[Dict]
    ) -> float:
        """
        Utility is the terminal state's Ω — how generative and complex the
        end state is.  Futures that open new possibilities are preferred.
        """
        if not steps:
            return 0.0
        return steps[-1].omega()

    def report(self) -> str:
        if not self._trajectory_history:
            return "No trajectories generated yet."
        lines = [
            f"=== TrajectoryEngine Report ===",
            f"  Total trajectories  : {len(self._trajectory_history)}",
            f"  Best score seen     : {max(t.score() for t in self._trajectory_history):.4f}",
            f"  Avg score           : {sum(t.score() for t in self._trajectory_history)/len(self._trajectory_history):.4f}",
        ]
        return "\n".join(lines)
