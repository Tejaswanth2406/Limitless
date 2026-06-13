"""Human-readable formatters for Limitless objects."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..agents.swarm import SwarmReport
    from ..core.node import TemporalNode


def format_state_tree(node: "TemporalNode", depth: int = 0) -> str:
    """Render a node's temporal trajectory as an indented tree."""
    indent = "  " * depth
    s = node.current_state
    lines = [
        f"{indent}╔══ {node.label or node.id[:8]}",
        f"{indent}║  entropy   = {s.entropy:.4f}",
        f"{indent}║  coherence = {s.coherence:.4f}",
        f"{indent}║  omega (Ω) = {s.omega():.4f}",
        f"{indent}║  momentum  = {s.momentum:.4f}",
        f"{indent}║  novelty   = {s.novelty:.4f}",
        f"{indent}║  history   = {len(node.state_history)} snapshots",
        f"{indent}╚══ edges → {list(node.edges.keys())[:5]}",
    ]
    return "\n".join(lines)


def format_swarm_report(report: "SwarmReport") -> str:
    """Render a SwarmReport as a formatted string."""
    sep = "─" * 60
    lines = [
        sep,
        f"  SWARM REPORT  [run={report.run_id}]",
        sep,
        f"  Nodes          : {report.node_count}",
        f"  Duration       : {report.duration_seconds:.4f}s",
        f"  Confidence     : {report.confidence():.2%}",
        f"  Agents run     : {len(report.agent_results)}",
        "",
        "  NARRATIVE",
        "  " + "·" * 56,
    ]

    narrative = report.narrative()
    # Word-wrap at 56 chars
    words = narrative.split()
    line_buf, current_len = [], 0
    for word in words:
        if current_len + len(word) + 1 > 56:
            lines.append("  " + " ".join(line_buf))
            line_buf, current_len = [word], len(word)
        else:
            line_buf.append(word)
            current_len += len(word) + 1
    if line_buf:
        lines.append("  " + " ".join(line_buf))

    risks = report.risks()
    if risks:
        lines += ["", "  RISKS", "  " + "·" * 56]
        for r in risks:
            lines.append(f"  ⚠  {r}")

    lines.append(sep)
    return "\n".join(lines)


def format_node_table(nodes: List["TemporalNode"]) -> str:
    """Render a table of nodes with key metrics."""
    header = f"{'Label':<20} {'Entropy':>8} {'Coherence':>10} {'Omega':>8} {'Momentum':>10}"
    divider = "─" * len(header)
    rows = [header, divider]
    for node in nodes:
        s = node.current_state
        rows.append(
            f"{(node.label or node.id[:8]):<20} "
            f"{s.entropy:>8.4f} "
            f"{s.coherence:>10.4f} "
            f"{s.omega():>8.4f} "
            f"{s.momentum:>10.4f}"
        )
    rows.append(divider)
    return "\n".join(rows)
