"""Tests for simulation, benchmarks, and visualiser."""

import math
from Limitless.core.node import TemporalNode
from Limitless.core.state import TemporalState
from Limitless.simulation.world import TemporalWorld
from Limitless.benchmarks.benchmark_runner import BenchmarkRunner
from Limitless.benchmarks.temporal_benchmarks import (
    BenchmarkOmegaConvergence,
    BenchmarkFieldPropagation,
    BenchmarkEntropyExpansion,
    BenchmarkTrajectoryAccuracy,
    BenchmarkSwarmLatency,
)
from Limitless.visualisation.field_visualiser import FieldVisualiser
from Limitless.engine.omega_optimizer import OmegaOptimizer
from Limitless.utils.serialiser import save_nodes, load_nodes, node_to_dict, node_from_dict
from Limitless.utils.logger import get_logger, Level
import tempfile, os


def _node(label, entropy=0.5):
    s = TemporalState(label=label, entropy=entropy, coherence=1.0 - entropy)
    return TemporalNode(label=label, current_state=s)


class TestBenchmarks:
    def test_omega_convergence_passes(self):
        b = BenchmarkOmegaConvergence()
        r = b.run()
        assert r.score > 0.9
        assert r.passed

    def test_field_propagation_runs(self):
        b = BenchmarkFieldPropagation()
        r = b.run()
        assert r.score >= 0.0
        assert r.error is None

    def test_entropy_expansion_passes(self):
        b = BenchmarkEntropyExpansion()
        r = b.run()
        assert r.passed

    def test_trajectory_accuracy_runs(self):
        b = BenchmarkTrajectoryAccuracy()
        r = b.run()
        assert r.error is None

    def test_swarm_latency_completes(self):
        b = BenchmarkSwarmLatency()
        r = b.run()
        assert r.error is None

    def test_benchmark_runner_all_complete(self):
        runner = BenchmarkRunner()
        runner.add_all([
            BenchmarkOmegaConvergence(),
            BenchmarkEntropyExpansion(),
        ])
        results = runner.run_all()
        assert len(results) == 2
        summary = runner.summary_dict()
        assert "avg_score" in summary


class TestOmegaOptimizer:
    def test_converges_to_half(self):
        optimizer = OmegaOptimizer(lr=0.05, max_steps=200, tol=1e-7)
        node = _node("x", entropy=0.1)
        result = optimizer.optimise(node)
        assert abs(result.optimal_entropy - 0.5) < 0.01

    def test_converges_from_high_entropy(self):
        optimizer = OmegaOptimizer(lr=0.05, max_steps=200, tol=1e-7)
        node = _node("y", entropy=0.9)
        result = optimizer.optimise(node)
        assert abs(result.optimal_entropy - 0.5) < 0.01

    def test_apply_shifts_node(self):
        optimizer = OmegaOptimizer()
        node = _node("z", entropy=0.1)
        before = node.current_state.entropy
        optimizer.optimise(node, apply=True)
        after = node.current_state.entropy
        assert after > before   # should have moved toward 0.5


class TestVisualiser:
    def test_entropy_bars_returns_string(self):
        vis = FieldVisualiser(width=50, color=False)
        nodes = [_node(f"n{i}", 0.3 + i * 0.1) for i in range(4)]
        out = vis.entropy_bars(nodes)
        assert isinstance(out, str)
        assert "n0" in out

    def test_sparkline_length(self):
        vis = FieldVisualiser(width=50, color=False)
        nodes = [_node("s", 0.5)]
        for _ in range(10):
            nodes[0].advance({}, entropy_shift=0.02)
        out = vis.trajectory_sparklines(nodes)
        assert isinstance(out, str)

    def test_phase_portrait_returns_string(self):
        vis = FieldVisualiser(width=50, color=False)
        nodes = [_node(f"p{i}", 0.2 + i * 0.2) for i in range(3)]
        out = vis.phase_portrait(nodes)
        assert isinstance(out, str)


class TestSerialiser:
    def test_node_roundtrip(self):
        node = _node("serial_test", entropy=0.6)
        node.advance({"x": 1}, entropy_shift=0.05)
        d = node_to_dict(node)
        restored = node_from_dict(d)
        assert restored.label == node.label
        assert abs(restored.current_state.entropy - node.current_state.entropy) < 1e-9

    def test_file_roundtrip(self):
        nodes = [_node(f"f{i}", 0.4) for i in range(3)]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_nodes(nodes, path)
            loaded = load_nodes(path)
            assert len(loaded) == 3
            assert loaded[0].label == "f0"
        finally:
            os.unlink(path)


class TestLogger:
    def test_logger_creation(self):
        log = get_logger("test.module", level=Level.DEBUG)
        log.info("hello")
        assert len(log.history()) >= 1

    def test_level_filtering(self):
        log = get_logger("test.filter", level=Level.ERROR)
        log.debug("should be filtered")
        log.info("also filtered")
        log.error("should pass")
        h = log.history(min_level=Level.ERROR)
        assert all(e["level"] == "ERROR" for e in h)
