#!/usr/bin/env python3
"""
Limitless CLI — command-line interface for the Temporal Reality Operating System.

Usage
-----
    python -m Limitless.cli demo
    python -m Limitless.cli benchmark
    python -m Limitless.cli scenario --entities market,sentiment --steps 20
    python -m Limitless.cli visualise --entities alpha,beta,gamma --ticks 10
"""

from __future__ import annotations

import argparse
import sys

from .api.limitless_api import Limitless
from .benchmarks.benchmark_runner import BenchmarkRunner
from .benchmarks.temporal_benchmarks import (
    BenchmarkOmegaConvergence,
    BenchmarkFieldPropagation,
    BenchmarkSwarmLatency,
    BenchmarkTrajectoryAccuracy,
    BenchmarkEntropyExpansion,
)
from .visualisation.field_visualiser import FieldVisualiser


def cmd_demo(args) -> None:
    """Run the built-in demo scenarios."""
    print("\n🌀  Limitless — Temporal Reality OS  🌀\n")
    lm = (
        Limitless("DemoWorld")
        .define("market",    {"price": 100.0, "volume": 5000}, entropy=0.35)
        .define("sentiment", {"score": 0.7},                    entropy=0.55)
        .define("macro",     {"gdp": 2.1, "inflation": 3.5},   entropy=0.45)
        .connect("market", "sentiment", weight=0.8)
        .connect("macro",  "market",    weight=0.6)
    )
    lm.observe("market", "text", "The market is showing signs of volatility")
    lm.tick(args.steps)
    lm.summary()
    report = lm.think()
    print(lm.render(report))


def cmd_benchmark(args) -> None:
    """Run the full benchmark suite."""
    runner = BenchmarkRunner()
    runner.add_all([
        BenchmarkOmegaConvergence(),
        BenchmarkFieldPropagation(),
        BenchmarkSwarmLatency(),
        BenchmarkTrajectoryAccuracy(),
        BenchmarkEntropyExpansion(),
    ])
    results = runner.run_all()
    runner.print_report(results)


def cmd_scenario(args) -> None:
    """Run a quick user-defined scenario from CLI args."""
    entity_labels = [e.strip() for e in args.entities.split(",")]
    lm = Limitless("CLIScenario")
    for i, label in enumerate(entity_labels):
        lm.define(label, {"index": float(i)}, entropy=0.3 + i * 0.1)
    for i in range(len(entity_labels) - 1):
        lm.connect(entity_labels[i], entity_labels[i + 1])

    lm.tick(args.steps)
    lm.summary()
    report = lm.think()
    print(lm.render(report))


def cmd_visualise(args) -> None:
    """Visualise a temporal field in the terminal."""
    entity_labels = [e.strip() for e in args.entities.split(",")]
    lm = Limitless("VisWorld")
    for i, label in enumerate(entity_labels):
        lm.define(label, {"v": float(i)}, entropy=0.2 + i * 0.15)
    for i in range(len(entity_labels) - 1):
        lm.connect(entity_labels[i], entity_labels[i + 1])

    lm.tick(args.ticks)
    vis = FieldVisualiser(width=64)
    print(vis.entropy_bars(lm.entities()))
    print(vis.trajectory_sparklines(lm.entities()))
    print(vis.phase_portrait(lm.entities()))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="limitless",
        description="Limitless — Temporal Reality Operating System CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # demo
    p_demo = sub.add_parser("demo", help="Run built-in demo scenario")
    p_demo.add_argument("--steps", type=int, default=10, help="Simulation steps")

    # benchmark
    sub.add_parser("benchmark", help="Run full benchmark suite")

    # scenario
    p_sc = sub.add_parser("scenario", help="Run a custom scenario")
    p_sc.add_argument("--entities", type=str, default="alpha,beta,gamma", help="Comma-separated entity names")
    p_sc.add_argument("--steps", type=int, default=15)

    # visualise
    p_vis = sub.add_parser("visualise", help="Visualise a temporal field")
    p_vis.add_argument("--entities", type=str, default="a,b,c,d")
    p_vis.add_argument("--ticks", type=int, default=10)

    args = parser.parse_args()

    dispatch = {
        "demo":       cmd_demo,
        "benchmark":  cmd_benchmark,
        "scenario":   cmd_scenario,
        "visualise":  cmd_visualise,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
