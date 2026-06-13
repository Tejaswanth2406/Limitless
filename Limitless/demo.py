#!/usr/bin/env python3
"""
demo.py — Limitless framework demonstration.

Runs three scenarios:
    1. Market-Sentiment world (basic API)
    2. Multi-entity linked world (field propagation)
    3. Counterfactual scenario fork (Scenario builder)
"""

from Limitless.api.limitless_api import Limitless
from Limitless.simulation.scenario import Scenario
from Limitless.utils.formatters import format_node_table


def demo_basic():
    print("\n" + "═" * 60)
    print("  DEMO 1: Basic Market-Sentiment World")
    print("═" * 60)

    lm = (
        Limitless("MarketWorld")
        .define("market",    {"price": 100.0, "volume": 5000},  entropy=0.35)
        .define("sentiment", {"score": 0.7, "variance": 0.1},   entropy=0.55)
        .define("macro",     {"gdp_growth": 2.1, "inflation": 3.5}, entropy=0.45)
        .connect("market", "sentiment", weight=0.8)
        .connect("macro",  "market",    weight=0.6)
        .connect("macro",  "sentiment", weight=0.4)
    )

    # Inject some observations
    lm.observe("market",    "text",    "The market is declining rapidly, investors are worried")
    lm.observe("sentiment", "numeric", {"score": 0.3, "variance": 0.4})
    lm.observe("macro",     "event",   {"type": "rate_hike", "severity": 0.7,
                                        "payload": {"rate": 5.5}})

    # Advance time
    lm.tick(10)
    lm.summary()

    # Reason
    report = lm.think()
    print(lm.render(report))

    # Project one entity
    print("\n  FUTURE PROJECTION: market")
    print(lm.project("market", horizon=4))
    print()


def demo_field_propagation():
    print("\n" + "═" * 60)
    print("  DEMO 2: Five-Node Field Propagation")
    print("═" * 60)

    lm = Limitless("PropagationWorld")
    labels = ["source", "relay_a", "relay_b", "sink_a", "sink_b"]
    entropies = [0.8, 0.5, 0.5, 0.2, 0.2]

    for label, ent in zip(labels, entropies):
        lm.define(label, {"val": ent * 100}, entropy=ent)

    # Topology: source → relays → sinks
    lm.connect("source",  "relay_a", 0.9)
    lm.connect("source",  "relay_b", 0.7)
    lm.connect("relay_a", "sink_a",  0.8)
    lm.connect("relay_b", "sink_b",  0.8)
    lm.connect("relay_a", "relay_b", 0.3)

    lm.observe("source", "text", "A high-entropy signal is propagating through the network")
    lm.tick(20)

    print(format_node_table(lm.entities()))
    report = lm.think()
    print(lm.render(report))


def demo_scenario_fork():
    print("\n" + "═" * 60)
    print("  DEMO 3: Counterfactual Scenario Fork")
    print("═" * 60)

    base = (
        Scenario("BaseTimeline")
        .add_entity("company", {"revenue": 1_000_000, "employees": 200}, entropy=0.3)
        .add_entity("market",  {"index": 4200},                           entropy=0.4)
        .add_link("market", "company", weight=0.7)
        .add_event("market", {"type": "text", "raw": "market conditions are stable"}, at_step=3)
    )

    # Fork: inject a crisis event instead
    crisis = base.fork("CrisisTimeline")
    crisis.add_event(
        "market",
        {"type": "event", "raw": {"type": "crash", "severity": 0.95,
                                   "payload": {"cause": "geopolitical"}}},
        at_step=3,
        priority=9.0,
    )

    print("  Running BASE timeline…")
    base.run(steps=8)
    base_nodes = list(base.world.entities())

    print("  Running CRISIS timeline…")
    crisis.run(steps=8)
    crisis_nodes = list(crisis.world.entities())

    print("\n  BASE timeline state:")
    print(format_node_table(base_nodes))

    print("\n  CRISIS timeline state:")
    print(format_node_table(crisis_nodes))

    # Compare final market entropy
    base_market   = base.world.entity("market")
    crisis_market = crisis.world.entity("market")
    if base_market and crisis_market:
        print(
            f"\n  Market entropy: base={base_market.current_state.entropy:.4f} "
            f"vs crisis={crisis_market.current_state.entropy:.4f}"
        )


if __name__ == "__main__":
    demo_basic()
    demo_field_propagation()
    demo_scenario_fork()
    print("\n✓ All demos complete.\n")
