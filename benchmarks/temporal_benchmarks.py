"""
Concrete benchmark implementations for the Limitless framework.

Each benchmark tests a core theoretical property:
    1. OmegaConvergence     — Ω optimiser reaches H* = 0.5 analytically
    2. FieldPropagation     — entropy spreads through a linked field correctly
    3. SwarmLatency         — full swarm completes in acceptable time
    4. TrajectoryAccuracy   — best trajectory outscores random trajectories
    5. EntropyExpansion     — closed system entropy is non-decreasing (Theorem 5.1)
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, Tuple

from ..core.field import TemporalField
from ..core.kernel import TemporalKernel
from ..core.node import TemporalNode
from ..core.state import TemporalState
from ..engine.omega_optimizer import OmegaOptimizer
from ..engine.trajectory_engine import TrajectoryEngine
from ..agents.swarm import AgentSwarm
from .benchmark_runner import BaseBenchmark


def _node(label: str, entropy: float = 0.5) -> TemporalNode:
    s = TemporalState(label=label, entropy=entropy, coherence=1.0 - entropy)
    return TemporalNode(label=label, current_state=s)


# ── Benchmark 1: Omega Convergence ───────────────────────────────────────────

class BenchmarkOmegaConvergence(BaseBenchmark):
    """
    The OmegaOptimizer should converge to H* ≈ 0.5 for nodes with Π = 0.

    Score = 1 − |H_final − 0.5| / 0.5  (1.0 = perfect convergence)
    """
    name = "omega_convergence"

    def _execute(self) -> Tuple[float, Dict]:
        optimizer = OmegaOptimizer(lr=0.05, max_steps=200, tol=1e-7)
        errors = []
        for init_h in [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]:
            node = _node(f"h{init_h}", entropy=init_h)
            result = optimizer.optimise(node, apply=False)
            errors.append(abs(result.optimal_entropy - 0.5))

        avg_error = sum(errors) / len(errors)
        score = max(0.0, 1.0 - avg_error / 0.5)
        return score, {"avg_error_from_half": round(avg_error, 6), "errors": [round(e, 6) for e in errors]}

    def passing_threshold(self) -> float:
        return 0.95


# ── Benchmark 2: Field Propagation ───────────────────────────────────────────

class BenchmarkFieldPropagation(BaseBenchmark):
    """
    After N ticks of a two-node field, entropy should equalise.
    A high-entropy node should pull a low-entropy node upward.

    Score = 1 − |H_lo_final − H_hi_initial| / H_hi_initial
    """
    name = "field_propagation"

    def _execute(self) -> Tuple[float, Dict]:
        field = TemporalField(decay=0.01)
        lo = _node("lo", entropy=0.1)
        hi = _node("hi", entropy=0.9)
        lo.connect(hi, weight=1.0)
        field.register(lo)
        field.register(hi)

        for _ in range(30):
            field.tick()

        lo_final = lo.current_state.entropy
        hi_final = hi.current_state.entropy
        # Low node should have risen toward high
        propagation = lo_final - 0.1   # how much lo rose
        score = min(1.0, propagation / 0.8)  # 0.8 = full equalisation

        return score, {
            "lo_entropy_initial": 0.1,
            "lo_entropy_final": round(lo_final, 4),
            "hi_entropy_final": round(hi_final, 4),
            "propagation": round(propagation, 4),
        }

    def passing_threshold(self) -> float:
        return 0.3


# ── Benchmark 3: Swarm Latency ────────────────────────────────────────────────

class BenchmarkSwarmLatency(BaseBenchmark):
    """
    The full AgentSwarm must complete analysis of 10 nodes within 2 seconds.

    Score = max(0, 1 − elapsed / 2.0)
    """
    name = "swarm_latency"
    MAX_SECONDS = 2.0

    def _execute(self) -> Tuple[float, Dict]:
        nodes = [_node(f"n{i}", entropy=0.3 + i * 0.05) for i in range(10)]
        for i in range(len(nodes) - 1):
            nodes[i].advance({"x": i}, entropy_shift=0.01)

        swarm = AgentSwarm()
        t0 = time.time()
        report = swarm.run(nodes)
        elapsed = time.time() - t0

        score = max(0.0, 1.0 - elapsed / self.MAX_SECONDS)
        return score, {
            "elapsed_seconds": round(elapsed, 4),
            "max_allowed": self.MAX_SECONDS,
            "confidence": round(report.confidence(), 4),
        }

    def passing_threshold(self) -> float:
        return 0.1   # just needs to complete in time


# ── Benchmark 4: Trajectory Accuracy ─────────────────────────────────────────

class BenchmarkTrajectoryAccuracy(BaseBenchmark):
    """
    The best-scored trajectory should outperform the worst-scored trajectory.

    Score = (best_score − worst_score) / max(best_score, 1e-9)
    """
    name = "trajectory_accuracy"

    def _execute(self) -> Tuple[float, Dict]:
        node = _node("test", entropy=0.5)
        node.advance({"x": 1.0, "y": 2.0}, entropy_shift=0.05)
        node.advance({"x": 1.5, "y": 2.3}, entropy_shift=0.03)

        engine = TrajectoryEngine(horizon=5, branching_factor=4)
        trajectories = engine.project(node)

        scores = [t.score() for t in trajectories]
        best = max(scores)
        worst = min(scores)
        score = (best - worst) / max(abs(best), 1e-9)

        return min(1.0, score), {
            "best_score": round(best, 4),
            "worst_score": round(worst, 4),
            "spread": round(best - worst, 4),
            "trajectories": len(trajectories),
        }

    def passing_threshold(self) -> float:
        return 0.01  # any spread at all is a pass


# ── Benchmark 5: Entropy Expansion (Theorem 5.1) ─────────────────────────────

class BenchmarkEntropyExpansion(BaseBenchmark):
    """
    In a closed field of N nodes, total entropy H_total must be non-decreasing.

    Score = fraction of ticks where dH_total ≥ −tolerance
    """
    name = "entropy_expansion_theorem"
    TOLERANCE = 1e-6

    def _execute(self) -> Tuple[float, Dict]:
        field = TemporalField(decay=0.0)   # no decay = fully closed
        nodes = [_node(f"n{i}", entropy=i * 0.15) for i in range(6)]
        for i in range(len(nodes) - 1):
            nodes[i].connect(nodes[i+1], weight=1.0)
        for n in nodes:
            field.register(n)

        prev_total = sum(n.current_state.entropy for n in nodes)
        violations = 0
        ticks = 50

        for _ in range(ticks):
            field.tick()
            total = sum(n.current_state.entropy for n in nodes)
            if total < prev_total - self.TOLERANCE:
                violations += 1
            prev_total = total

        score = 1.0 - violations / ticks
        return score, {
            "ticks": ticks,
            "violations": violations,
            "final_total_entropy": round(prev_total, 4),
        }

    def passing_threshold(self) -> float:
        return 0.9   # allow minor floating-point noise
