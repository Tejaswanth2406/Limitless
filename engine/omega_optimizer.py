"""
OmegaOptimizer — finds the state transitions that maximise the Omega functional Ω.

In the Limitless framework, Ω = C · H · (1 + Π) is the measure of generative complexity.
The OmegaOptimizer performs gradient ascent in state space to find configurations that
are simultaneously coherent AND open — the edge of chaos where the most interesting
dynamics occur.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..core.node import TemporalNode
from ..core.state import TemporalState


@dataclass
class OptimizationResult:
    """Result of one Omega optimisation run."""
    node_label: str
    initial_omega: float
    final_omega: float
    steps_taken: int
    converged: bool
    omega_trajectory: List[float] = field(default_factory=list)
    optimal_entropy: float = 0.5
    improvement: float = 0.0

    def __post_init__(self):
        self.improvement = self.final_omega - self.initial_omega

    def summary(self) -> str:
        status = "CONVERGED" if self.converged else "MAX_STEPS"
        return (
            f"OmegaOpt [{self.node_label}] {status}: "
            f"Ω {self.initial_omega:.4f} → {self.final_omega:.4f} "
            f"(+{self.improvement:.4f}) in {self.steps_taken} steps, "
            f"optimal H*={self.optimal_entropy:.4f}"
        )


class OmegaOptimizer:
    """
    Gradient-ascent optimiser for the Omega functional.

    For a given node, the optimiser searches the (H, Π) subspace for the
    configuration that maximises Ω = (1-H) · H · (1 + Π).

    The analytical optimum for fixed Π is:
        H* = (1 + Π) / (2 · (1 + Π)) = 0.5       [when Π = 0]
        H* → 0.5 from above as Π increases         [always > 0.5]

    The optimiser additionally applies entropy-shifting transitions to nodes
    to move them toward their optimal configuration.
    """

    def __init__(self, lr: float = 0.05, max_steps: int = 100, tol: float = 1e-5):
        """
        Parameters
        ----------
        lr:         Learning rate for gradient ascent.
        max_steps:  Maximum optimisation steps.
        tol:        Convergence tolerance on ΔΩ.
        """
        self.lr = lr
        self.max_steps = max_steps
        self.tol = tol
        self._results: List[OptimizationResult] = []

    # ── Single-node optimisation ───────────────────────────────────────────────

    def optimise(self, node: TemporalNode, apply: bool = False) -> OptimizationResult:
        """
        Find the entropy value H* that maximises Ω for this node.

        Parameters
        ----------
        node:   Node to optimise.
        apply:  If True, apply the entropy shift to transition the node toward H*.
        """
        s = node.current_state
        pi = len(s.potential_paths) / max(1, len(s.potential_paths) + 1)
        h_star = self._analytical_optimum(pi)

        initial_omega = s.omega()
        trajectory = [initial_omega]

        h = s.entropy
        prev_omega = initial_omega
        converged = False

        for step in range(self.max_steps):
            omega = self._omega(h, pi)
            grad = self._domega_dh(h, pi)
            h = max(0.001, min(0.999, h + self.lr * grad))
            new_omega = self._omega(h, pi)
            trajectory.append(new_omega)

            if abs(new_omega - prev_omega) < self.tol:
                converged = True
                break
            prev_omega = new_omega

        if apply:
            shift = h - s.entropy
            node.advance({}, entropy_shift=shift)

        result = OptimizationResult(
            node_label=node.label or node.id[:8],
            initial_omega=initial_omega,
            final_omega=self._omega(h, pi),
            steps_taken=len(trajectory) - 1,
            converged=converged,
            omega_trajectory=trajectory,
            optimal_entropy=round(h_star, 4),
        )
        self._results.append(result)
        return result

    def optimise_field(
        self, nodes: List[TemporalNode], apply: bool = False
    ) -> List[OptimizationResult]:
        """Optimise all nodes in a field and return sorted results (best improvement first)."""
        results = [self.optimise(n, apply=apply) for n in nodes]
        results.sort(key=lambda r: -r.improvement)
        return results

    # ── Analytical helpers ─────────────────────────────────────────────────────

    def _analytical_optimum(self, pi: float) -> float:
        """
        Analytical solution: dΩ/dH = 0
        Ω = (1-H)·H·(1+Π)
        dΩ/dH = (1+Π)·(1 - 2H) = 0  ⟹  H* = 0.5
        Exactly 0.5 regardless of Π (Π only scales Ω, not the optimum location).
        """
        return 0.5

    def _omega(self, h: float, pi: float) -> float:
        c = 1.0 - h
        return c * h * (1.0 + pi)

    def _domega_dh(self, h: float, pi: float) -> float:
        """Gradient of Ω w.r.t. H: dΩ/dH = (1+Π)·(1 - 2H)"""
        return (1.0 + pi) * (1.0 - 2.0 * h)

    def report(self) -> str:
        if not self._results:
            return "No optimisations run yet."
        lines = ["=== OmegaOptimizer Report ==="]
        for r in self._results[-10:]:
            lines.append("  " + r.summary())
        return "\n".join(lines)

    def last_result(self) -> Optional[OptimizationResult]:
        return self._results[-1] if self._results else None
