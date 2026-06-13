"""Tests for Limitless engines."""

import pytest
from Limitless.core.node import TemporalNode
from Limitless.core.state import TemporalState
from Limitless.engine.entropy_engine import EntropyEngine
from Limitless.engine.trajectory_engine import TrajectoryEngine
from Limitless.engine.reality_compiler import RealityCompiler


def _make_node(label: str, entropy: float = 0.5) -> TemporalNode:
    s = TemporalState(label=label, entropy=entropy, coherence=1.0 - entropy)
    return TemporalNode(label=label, current_state=s)


class TestEntropyEngine:
    def test_score_returns_all_keys(self):
        engine = EntropyEngine()
        node = _make_node("a")
        score = engine.score(node)
        for key in ("entropy", "coherence", "novelty", "momentum", "omega", "importance"):
            assert key in score

    def test_rank_nodes_descending(self):
        engine = EntropyEngine()
        nodes = [_make_node("lo", 0.1), _make_node("hi", 0.9), _make_node("mid", 0.5)]
        ranked = engine.rank_nodes(nodes)
        scores = [s for _, s in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_allocate_compute_sums_to_budget(self):
        engine = EntropyEngine()
        nodes = [_make_node(str(i), i * 0.2) for i in range(1, 5)]
        alloc = engine.allocate_compute(nodes, total_budget=1.0)
        assert abs(sum(alloc.values()) - 1.0) < 1e-6

    def test_detect_phase_transition(self):
        engine = EntropyEngine()
        node = _make_node("volatile", 0.1)
        # Push a high-entropy state into history
        low = TemporalState(entropy=0.1)
        node.state_history.append(low)
        node.current_state.entropy = 0.9
        transitions = engine.detect_phase_transition([node], threshold=0.3)
        assert node in transitions


class TestTrajectoryEngine:
    def test_project_returns_trajectories(self):
        engine = TrajectoryEngine(horizon=3, branching_factor=2)
        node = _make_node("x", 0.5)
        trajectories = engine.project(node)
        assert len(trajectories) == 2

    def test_trajectories_sorted_by_score(self):
        engine = TrajectoryEngine(horizon=3, branching_factor=3)
        node = _make_node("x", 0.5)
        trajectories = engine.project(node)
        scores = [t.score() for t in trajectories]
        assert scores == sorted(scores, reverse=True)

    def test_select_best(self):
        engine = TrajectoryEngine(horizon=3, branching_factor=3)
        node = _make_node("x", 0.5)
        trajectories = engine.project(node)
        best = engine.select_best(trajectories)
        assert best is not None
        assert best.score() == max(t.score() for t in trajectories)

    def test_trajectory_has_correct_steps(self):
        engine = TrajectoryEngine(horizon=4, branching_factor=2)
        node = _make_node("x")
        trajectories = engine.project(node)
        for t in trajectories:
            assert len(t.steps) == 4


class TestRealityCompiler:
    def test_compile_text_returns_delta(self):
        compiler = RealityCompiler()
        delta, entropy_shift = compiler.compile("text", "the company is losing money fast")
        assert "sentiment" in delta
        assert isinstance(entropy_shift, float)

    def test_compile_numeric(self):
        compiler = RealityCompiler()
        delta, entropy_shift = compiler.compile("numeric", {"price": 100.0, "volume": 50.0})
        assert "mean" in delta
        assert entropy_shift >= 0.0

    def test_compile_event(self):
        compiler = RealityCompiler()
        event = {"type": "crash", "severity": 0.9, "payload": {"asset": "BTC"}}
        delta, entropy_shift = compiler.compile("event", event)
        assert entropy_shift > 0.1  # high severity → high entropy

    def test_compile_signal(self):
        compiler = RealityCompiler()
        signal = {"name": "temperature", "value": 120.0, "previous": 100.0}
        delta, entropy_shift = compiler.compile("signal", signal)
        assert delta["change"] == pytest.approx(20.0)

    def test_compile_batch(self):
        compiler = RealityCompiler()
        batch = [
            {"type": "text", "raw": "things are good", "source": "news"},
            {"type": "numeric", "raw": {"x": 5.0}, "source": "sensor"},
        ]
        results = compiler.compile_batch(batch)
        assert len(results) == 2
