"""SynthesizerAgent — integrates all other agent findings into a coherent report."""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.node import TemporalNode
from .base_agent import AgentResult, BaseAgent


class SynthesizerAgent(BaseAgent):
    """
    Integrates findings from Observer, Historian, and Futurist agents into
    a coherent, actionable report.

    The Synthesizer answers: *What does everything mean together?*
    """

    def run(
        self,
        nodes: List[TemporalNode],
        agent_results: List[AgentResult] = None,
        **kwargs,
    ) -> AgentResult:
        agent_results = agent_results or []

        # Collect findings by agent type
        by_type: Dict[str, Dict] = {}
        for result in agent_results:
            by_type[result.agent_type] = result.findings

        # Build integrated narrative
        narrative_parts = []

        observer_data = by_type.get("Observer", {})
        if observer_data:
            avg_h = observer_data.get("avg_entropy", "N/A")
            most_chaotic = observer_data.get("most_chaotic", "N/A")
            most_ordered = observer_data.get("most_ordered", "N/A")
            narrative_parts.append(
                f"Current field state: avg entropy={avg_h}, "
                f"most chaotic node='{most_chaotic}', "
                f"most ordered node='{most_ordered}'."
            )

        historian_data = by_type.get("Historian", {})
        if historian_data:
            histories = historian_data.get("histories", {})
            trending_up = [
                k for k, v in histories.items()
                if isinstance(v, dict) and v.get("entropy_trend", 0) > 0.01
            ]
            trending_down = [
                k for k, v in histories.items()
                if isinstance(v, dict) and v.get("entropy_trend", 0) < -0.01
            ]
            narrative_parts.append(
                f"Temporal trends: {len(trending_up)} nodes increasing in entropy "
                f"({', '.join(trending_up[:3]) or 'none'}), "
                f"{len(trending_down)} decreasing "
                f"({', '.join(trending_down[:3]) or 'none'})."
            )

        futurist_data = by_type.get("Futurist", {})
        if futurist_data:
            projections = futurist_data.get("projections", {})
            high_future_omega = [
                k for k, v in projections.items()
                if isinstance(v, dict) and (v.get("best_terminal_omega") or 0) > 0.3
            ]
            narrative_parts.append(
                f"Future projections: {len(projections)} nodes projected. "
                f"High generative potential nodes: "
                f"{', '.join(high_future_omega[:3]) or 'none'}."
            )

        # Risk flags
        risks = self._detect_risks(nodes, by_type)

        findings = {
            "narrative": " ".join(narrative_parts) or "Insufficient data for synthesis.",
            "agent_results_integrated": len(agent_results),
            "risks": risks,
            "node_count": len(nodes),
            "overall_confidence": self._aggregate_confidence(agent_results),
            "raw_by_type": {k: list(v.keys()) for k, v in by_type.items()},
        }

        result = AgentResult(
            agent_id=self.id,
            agent_type="Synthesizer",
            findings=findings,
            confidence=self._aggregate_confidence(agent_results),
            notes="Synthesis complete.",
        )
        return self._record(result)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _detect_risks(
        self, nodes: List[TemporalNode], by_type: Dict
    ) -> List[str]:
        risks = []

        # High entropy average → system is near chaotic
        avg_entropy = sum(n.current_state.entropy for n in nodes) / max(1, len(nodes))
        if avg_entropy > 0.75:
            risks.append(f"HIGH GLOBAL ENTROPY ({avg_entropy:.2f}) — system approaching chaos.")

        # Any node with very high momentum
        volatile = [n for n in nodes if abs(n.current_state.momentum) > 0.5]
        if volatile:
            risks.append(
                f"{len(volatile)} node(s) with extreme momentum: "
                f"{[n.label for n in volatile[:3]]}"
            )

        # No history — we're blind
        no_history = [n for n in nodes if not n.state_history]
        if no_history:
            risks.append(
                f"{len(no_history)} node(s) have no historical data — predictions unreliable."
            )

        return risks

    def _aggregate_confidence(self, results: List[AgentResult]) -> float:
        if not results:
            return 0.0
        return sum(r.confidence for r in results) / len(results)
