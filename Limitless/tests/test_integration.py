"""Integration tests — full pipeline from API to SwarmReport."""

import pytest
from Limitless.api.limitless_api import Limitless
from Limitless.simulation.scenario import Scenario
from Limitless.simulation.world import TemporalWorld


class TestLimitlessAPI:
    def test_fluent_chain(self):
        lm = (
            Limitless("TestWorld")
            .define("market", {"price": 100.0}, entropy=0.35)
            .define("news", {"sentiment": 0.5}, entropy=0.6)
            .connect("market", "news")
        )
        assert len(lm.entities()) == 2

    def test_observe_and_tick(self):
        lm = Limitless()
        lm.define("economy", {"gdp": 1000}, entropy=0.4)
        lm.observe("economy", "text", "The economy is growing steadily")
        lm.tick(3)
        assert lm.step_count == 3

    def test_think_returns_report(self):
        lm = Limitless()
        lm.define("a", {"x": 1}, entropy=0.5)
        lm.define("b", {"y": 2}, entropy=0.4)
        lm.tick(2)
        report = lm.think()
        assert report is not None
        assert report.confidence() >= 0.0

    def test_render_returns_string(self):
        lm = Limitless()
        lm.define("x", {}, entropy=0.5)
        lm.tick(1)
        report = lm.think()
        rendered = lm.render(report)
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_snapshot(self):
        lm = Limitless()
        lm.define("node1", {"val": 42})
        lm.tick(1)
        snap = lm.snapshot()
        assert "nodes" in snap
        assert snap["node_count"] == 1

    def test_project(self):
        lm = Limitless()
        lm.define("stock", {"price": 200.0}, entropy=0.5)
        lm.tick(2)
        result = lm.project("stock", horizon=3)
        assert "stock" in result or "Best" in result

    def test_project_missing_entity(self):
        lm = Limitless()
        result = lm.project("nonexistent")
        assert "not found" in result


class TestScenario:
    def test_scenario_build_and_run(self):
        s = (
            Scenario("TestScenario")
            .add_entity("alpha", {"val": 1.0}, entropy=0.3)
            .add_entity("beta",  {"val": 2.0}, entropy=0.6)
            .add_link("alpha", "beta", weight=0.9)
            .add_event("alpha", {"type": "text", "raw": "alpha is failing"}, at_step=2)
        )
        s.run(steps=5)
        assert s.world is not None
        assert s.world._step_count == 5

    def test_scenario_fork(self):
        s = Scenario("Base").add_entity("x", entropy=0.5)
        fork = s.fork("Forked")
        assert fork.name == "Forked"
        assert len(fork._entity_specs) == 1
        # Modifying fork should not affect base
        fork.add_entity("extra", entropy=0.3)
        assert len(s._entity_specs) == 1


class TestTemporalWorld:
    def test_world_summary(self, capsys):
        world = TemporalWorld("W")
        world.add_entity("e1", {"v": 1}, entropy=0.4)
        world.step(2)
        world.print_summary()
        captured = capsys.readouterr()
        assert "W" in captured.out

    def test_analyse_returns_report(self):
        world = TemporalWorld("W2")
        world.add_entity("n1", {}, entropy=0.5)
        world.step(1)
        report = world.analyse()
        assert report.node_count == 1
