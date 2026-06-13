"""Tests for core temporal primitives."""

import math
import pytest
from Limitless.core.state import TemporalState
from Limitless.core.node import TemporalNode
from Limitless.core.field import TemporalField
from Limitless.core.kernel import TemporalKernel


class TestTemporalState:
    def test_default_creation(self):
        s = TemporalState()
        assert 0.0 <= s.entropy <= 1.0
        assert 0.0 <= s.coherence <= 1.0
        assert s.id is not None

    def test_transition_creates_new_state(self):
        s = TemporalState(state_vector={"x": 1.0}, entropy=0.5)
        s2 = s.transition({"x": 2.0})
        assert s2.state_vector["x"] == 2.0
        assert s.state_vector["x"] == 1.0  # original unchanged
        assert len(s2.history) == 1

    def test_transition_archives_history(self):
        s = TemporalState(state_vector={"a": 1})
        s2 = s.transition({"a": 2})
        s3 = s2.transition({"a": 3})
        assert len(s3.history) == 2

    def test_entropy_bounds(self):
        s = TemporalState(entropy=0.9)
        s2 = s.transition({}, entropy_shift=0.5)
        assert s2.entropy <= 1.0
        s3 = TemporalState(entropy=0.1).transition({}, entropy_shift=-0.5)
        assert s3.entropy >= 0.0

    def test_omega_positive(self):
        s = TemporalState(entropy=0.5, coherence=0.5)
        assert s.omega() >= 0.0

    def test_coherence_equals_one_minus_entropy_on_transition(self):
        s = TemporalState(entropy=0.3)
        s2 = s.transition({}, entropy_shift=0.1)
        assert abs(s2.coherence - (1.0 - s2.entropy)) < 1e-9

    def test_importance_score_range(self):
        s = TemporalState(entropy=0.5, momentum=0.2, novelty=0.3)
        imp = s.compute_importance()
        assert 0.0 <= imp <= 1.0


class TestTemporalNode:
    def test_advance_updates_state(self):
        node = TemporalNode(label="test")
        node.current_state.state_vector["v"] = 10
        node.advance({"v": 20})
        assert node.current_state.state_vector["v"] == 20
        assert len(node.state_history) == 1

    def test_temporal_distance_self_is_zero(self):
        node = TemporalNode(label="a")
        assert node.temporal_distance(node) == 0.0

    def test_connect_creates_bidirectional_edge(self):
        a = TemporalNode(label="a")
        b = TemporalNode(label="b")
        a.connect(b, weight=0.7)
        assert b.id in a.edges
        assert a.id in b.edges
        assert a.edges[b.id] == 0.7

    def test_field_influence_positive(self):
        a = TemporalNode(label="a")
        b = TemporalNode(label="b")
        b.current_state.entropy = 0.8
        inf = a.field_influence(b)
        assert inf >= 0.0


class TestTemporalField:
    def test_register_and_tick(self):
        field = TemporalField()
        node = TemporalNode(label="n1")
        field.register(node)
        field.tick()
        assert field.tick_count == 1

    def test_find_resonant_pairs(self):
        field = TemporalField()
        a = TemporalNode(label="a")
        b = TemporalNode(label="b")
        # Make them identical in temporal space
        a.current_state.entropy = 0.5
        b.current_state.entropy = 0.5
        a.current_state.coherence = 0.5
        b.current_state.coherence = 0.5
        a.current_state.momentum = 0.0
        b.current_state.momentum = 0.0
        field.register(a)
        field.register(b)
        pairs = field.find_resonant_pairs(threshold=0.01)
        assert len(pairs) >= 1

    def test_deregister(self):
        field = TemporalField()
        node = TemporalNode(label="x")
        field.register(node)
        field.deregister(node.id)
        assert node.id not in field.nodes


class TestTemporalKernel:
    def test_spawn_node(self):
        kernel = TemporalKernel()
        node = kernel.spawn_node("entity_a", {"value": 42}, entropy=0.4)
        assert node.label == "entity_a"
        assert node.id in kernel.field.nodes

    def test_ingest_and_process(self):
        kernel = TemporalKernel()
        kernel.spawn_node("src", {"x": 1})
        kernel.ingest("src", {"x": 99})
        processed = kernel.process_events()
        assert processed == 1

    def test_snapshot(self):
        kernel = TemporalKernel()
        kernel.spawn_node("n")
        snap = kernel.snapshot()
        assert "tick" in snap
        assert "global_entropy" in snap
        assert "nodes" in snap

    def test_tick_increments(self):
        kernel = TemporalKernel()
        kernel.spawn_node("n")
        kernel.tick()
        kernel.tick()
        assert kernel.field.tick_count == 2
