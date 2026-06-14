"""Temporal reasoning agents — the swarm cognition layer of Limitless."""
from .base_agent import BaseAgent
from .observer import ObserverAgent
from .historian import HistorianAgent
from .futurist import FuturistAgent
from .synthesizer import SynthesizerAgent
from .swarm import AgentSwarm
from .contradiction_hunter import ContradictionHunterAgent
from .novelty_agent import NoveltyAgent

__all__ = [
    "BaseAgent", "ObserverAgent", "HistorianAgent",
    "FuturistAgent", "SynthesizerAgent", "AgentSwarm",
    "ContradictionHunterAgent", "NoveltyAgent",
]
