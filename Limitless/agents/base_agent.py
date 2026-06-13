"""BaseAgent — abstract foundation for all Limitless agents."""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.node import TemporalNode


@dataclass
class AgentResult:
    """Structured output from any agent."""
    agent_id: str
    agent_type: str
    timestamp: float = field(default_factory=time.time)
    findings: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    notes: str = ""

    def __repr__(self) -> str:
        return (
            f"AgentResult({self.agent_type}, "
            f"confidence={self.confidence:.2f}, "
            f"findings={list(self.findings.keys())})"
        )


class BaseAgent(ABC):
    """
    Abstract base for all Limitless agents.

    Each agent specialises in one mode of temporal reasoning:
        - ObserverAgent   : extracts current state facts
        - HistorianAgent  : reconstructs the past trajectory
        - FuturistAgent   : projects future trajectories
        - SynthesizerAgent: integrates all agent findings
    """

    def __init__(self, label: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.label = label or self.__class__.__name__
        self.created_at = time.time()
        self._results: List[AgentResult] = []

    @abstractmethod
    def run(self, nodes: List[TemporalNode], **kwargs) -> AgentResult:
        """Execute the agent's reasoning task and return structured findings."""
        ...

    def history(self) -> List[AgentResult]:
        """All results this agent has produced."""
        return list(self._results)

    def last_result(self) -> Optional[AgentResult]:
        return self._results[-1] if self._results else None

    def _record(self, result: AgentResult) -> AgentResult:
        self._results.append(result)
        return result

    def uptime(self) -> float:
        return time.time() - self.created_at

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id[:8]}, runs={len(self._results)})"
