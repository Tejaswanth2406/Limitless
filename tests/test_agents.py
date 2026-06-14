"""Tests for Limitless agents."""

from Limitless.core.node import TemporalNode
from Limitless.core.state import TemporalState
from Limitless.agents.contradiction_hunter import ContradictionHunterAgent
from Limitless.agents.novelty_agent import NoveltyAgent


def _node(label: str, entropy: float = 0.5) -> TemporalNode:
    s = TemporalState(label=label, entropy=entropy, coherence=1.0 - entropy)
    return TemporalNode(label=label, current_state=s)


class TestContradictionHunter:
    def test_clean_nodes_no_contradictions(self):
        agent = ContradictionHunterAgent()
        nodes = [_node("a", 0.4), _node("b", 0.6)]
        result = agent.run(nodes)
        assert result.findings["clean"] is True
        assert result.confidence > 0.8

    def test_detects_coherence_entropy_mismatch(self):
        agent = ContradictionHunterAgent(tolerance=0.01)
        node = _node("bad", 0.5)
        node.current_state.coherence = 0.3   # should be 0.5 — mismatch
        result = agent.run([node])
        types = [c["type"] for c in result.findings["contradictions"]]
        assert "coherence_entropy_mismatch" in types

    def test_detects_ungrounded_momentum(self):
        agent = ContradictionHunterAgent()
        node = _node("fast", 0.5)
        node.current_state.momentum = 0.9   # high momentum, no history
        result = agent.run([node])
        types = [c["type"] for c in result.findings["contradictions"]]
        assert "ungrounded_momentum" in types

    def test_severity_zero_for_clean(self):
        agent = ContradictionHunterAgent()
        nodes = [_node(f"n{i}", 0.5) for i in range(5)]
        result = agent.run(nodes)
        assert result.findings["severity"] == 0.0


class TestNoveltyAgent:
    def test_high_novelty_node_flagged(self):
        agent = NoveltyAgent(novelty_threshold=0.1)
        node = _node("new", 0.5)
        node.current_state.novelty = 0.9
        result = agent.run([node])
        assert result.findings["frontier_count"] >= 1

    def test_stable_node_not_novel(self):
        agent = NoveltyAgent(novelty_threshold=0.5)
        node = _node("stable", 0.5)
        node.current_state.novelty = 0.0
        node.current_state.momentum = 0.0
        # Push some boring history
        for _ in range(5):
            node.advance({}, entropy_shift=0.0)
        result = agent.run([node])
        novel = [n["node"] for n in result.findings["novel_nodes"]]
        assert "stable" not in novel

    def test_global_novelty_in_range(self):
        agent = NoveltyAgent()
        nodes = [_node(f"n{i}", 0.5) for i in range(4)]
        result = agent.run(nodes)
        assert 0.0 <= result.findings["global_novelty"] <= 1.0
