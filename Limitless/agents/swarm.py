"""
AgentSwarm — orchestrates the full multi-agent temporal reasoning pipeline.

The swarm runs each specialist agent in sequence and passes their results
to the SynthesizerAgent for integration.  It returns a single coherent
intelligence report derived from all temporal perspectives.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.node import TemporalNode
from .base_agent import AgentResult
from .futurist import FuturistAgent
from .historian import HistorianAgent
from .observer import ObserverAgent
from .synthesizer import SynthesizerAgent


@dataclass
class SwarmReport:
    """Complete output from one swarm run."""
    run_id: str
    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    agent_results: List[AgentResult] = field(default_factory=list)
    synthesis: Optional[AgentResult] = None
    node_count: int = 0

    def narrative(self) -> str:
        if self.synthesis:
            return self.synthesis.findings.get("narrative", "No narrative generated.")
        return "No synthesis available."

    def risks(self) -> List[str]:
        if self.synthesis:
            return self.synthesis.findings.get("risks", [])
        return []

    def confidence(self) -> float:
        if self.synthesis:
            return self.synthesis.confidence
        return 0.0

    def __repr__(self) -> str:
        return (
            f"SwarmReport(agents={len(self.agent_results)}, "
            f"confidence={self.confidence():.2f}, "
            f"duration={self.duration_seconds:.3f}s)"
        )


class AgentSwarm:
    """
    Temporal Intelligence Swarm.

    Orchestrates:
        Observer → Historian → Futurist → Synthesizer

    Each agent processes the same set of nodes; results cascade through
    the pipeline and are unified by the Synthesizer.
    """

    def __init__(
        self,
        trajectory_horizon: int = 5,
        trajectory_branches: int = 3,
    ):
        self.observer = ObserverAgent()
        self.historian = HistorianAgent()
        self.futurist = FuturistAgent(
            horizon=trajectory_horizon,
            branches=trajectory_branches,
        )
        self.synthesizer = SynthesizerAgent()
        self._reports: List[SwarmReport] = []

    def run(
        self,
        nodes: List[TemporalNode],
        context: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> SwarmReport:
        """
        Execute the full swarm pipeline on *nodes*.

        Parameters
        ----------
        nodes:
            TemporalNodes to analyse.
        context:
            Optional external context passed to the Futurist.
        run_id:
            Optional label for this swarm run.

        Returns
        -------
        SwarmReport
        """
        import uuid
        run_id = run_id or str(uuid.uuid4())[:8]
        t0 = time.time()

        # --- Stage 1: Observe ---
        obs_result = self.observer.run(nodes)

        # --- Stage 2: History ---
        hist_result = self.historian.run(nodes)

        # --- Stage 3: Project futures ---
        fut_result = self.futurist.run(nodes, context=context)

        # --- Stage 4: Synthesize ---
        agent_results = [obs_result, hist_result, fut_result]
        syn_result = self.synthesizer.run(nodes, agent_results=agent_results)

        report = SwarmReport(
            run_id=run_id,
            duration_seconds=time.time() - t0,
            agent_results=agent_results,
            synthesis=syn_result,
            node_count=len(nodes),
        )
        self._reports.append(report)
        return report

    def run_history(self) -> List[SwarmReport]:
        return list(self._reports)

    def last_report(self) -> Optional[SwarmReport]:
        return self._reports[-1] if self._reports else None

    def print_report(self, report: SwarmReport) -> None:
        print("=" * 60)
        print(f"  SWARM REPORT  [{report.run_id}]")
        print("=" * 60)
        print(f"  Nodes analysed : {report.node_count}")
        print(f"  Duration       : {report.duration_seconds:.3f}s")
        print(f"  Confidence     : {report.confidence():.2f}")
        print()
        print("  NARRATIVE")
        print("  " + "-" * 56)
        print("  " + report.narrative())
        print()
        if report.risks():
            print("  RISKS")
            print("  " + "-" * 56)
            for risk in report.risks():
                print(f"  ⚠  {risk}")
        print("=" * 60)
