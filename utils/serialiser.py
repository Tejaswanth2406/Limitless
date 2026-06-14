"""
Serialiser — JSON-based persistence for Limitless objects.

Supports round-trip serialisation of:
    - TemporalState
    - TemporalNode
    - SwarmReport
    - World snapshots
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from ..core.state import TemporalState
from ..core.node import TemporalNode


# ── TemporalState ─────────────────────────────────────────────────────────────

def state_to_dict(s: TemporalState) -> Dict[str, Any]:
    return {
        "id": s.id,
        "label": s.label,
        "timestamp": s.timestamp,
        "state_vector": s.state_vector,
        "entropy": s.entropy,
        "coherence": s.coherence,
        "momentum": s.momentum,
        "novelty": s.novelty,
        "history": [state_to_dict(h) for h in s.history] if s.history else [],
        "metadata": s.metadata,
    }


def state_from_dict(d: Dict[str, Any]) -> TemporalState:
    s = TemporalState(
        id=d.get("id", ""),
        label=d.get("label", ""),
        timestamp=d.get("timestamp", 0.0),
        state_vector=d.get("state_vector", {}),
        entropy=d.get("entropy", 0.5),
        coherence=d.get("coherence", 0.5),
        momentum=d.get("momentum", 0.0),
        novelty=d.get("novelty", 0.0),
        metadata=d.get("metadata", {}),
    )
    s.history = [state_from_dict(h) for h in d.get("history", [])]
    return s


# ── TemporalNode ──────────────────────────────────────────────────────────────

def node_to_dict(node: TemporalNode) -> Dict[str, Any]:
    return {
        "id": node.id,
        "label": node.label,
        "current_state": state_to_dict(node.current_state),
        "state_history": [state_to_dict(s) for s in node.state_history],
        "edges": node.edges,
        "created_at": node.created_at,
    }


def node_from_dict(d: Dict[str, Any]) -> TemporalNode:
    node = TemporalNode(
        id=d.get("id", ""),
        label=d.get("label", ""),
        current_state=state_from_dict(d["current_state"]),
        edges=d.get("edges", {}),
        created_at=d.get("created_at", 0.0),
    )
    node.state_history = [state_from_dict(s) for s in d.get("state_history", [])]
    return node


# ── File I/O ──────────────────────────────────────────────────────────────────

def save_nodes(nodes: List[TemporalNode], path: str) -> None:
    """Serialise a list of nodes to a JSON file."""
    data = {"nodes": [node_to_dict(n) for n in nodes]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_nodes(path: str) -> List[TemporalNode]:
    """Deserialise nodes from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [node_from_dict(d) for d in data.get("nodes", [])]


def save_snapshot(snapshot: Dict[str, Any], path: str) -> None:
    """Write a kernel/world snapshot to JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)


def load_snapshot(path: str) -> Dict[str, Any]:
    """Load a snapshot from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_report(report: Any, path: str) -> None:
    """Serialise a SwarmReport's findings to JSON."""
    data = {
        "run_id": report.run_id,
        "timestamp": report.timestamp,
        "duration_seconds": report.duration_seconds,
        "node_count": report.node_count,
        "confidence": report.confidence(),
        "narrative": report.narrative(),
        "risks": report.risks(),
        "agent_findings": {
            r.agent_type: r.findings for r in report.agent_results
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
