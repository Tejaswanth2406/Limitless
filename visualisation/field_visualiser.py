"""
FieldVisualiser — renders the Temporal Field and node trajectories as ASCII art.

Produces rich terminal output without external dependencies.  Charts include:
    - Entropy heatmap (per-node bar chart)
    - Omega complexity map
    - Entropy trajectory over time (sparkline)
    - Field influence matrix (ASCII heatmap)
    - Phase-space portrait (entropy vs momentum)
"""

from __future__ import annotations

import math
from typing import List, Optional

from ..core.node import TemporalNode
from ..core.field import TemporalField


# ── Palette ───────────────────────────────────────────────────────────────────
BLOCK   = "█"
HALF    = "▌"
LIGHT   = "░"
MED     = "▒"
DARK    = "▓"
FILL    = [" ", LIGHT, MED, DARK, BLOCK]
SPARKS  = "▁▂▃▄▅▆▇█"


class FieldVisualiser:
    """
    Terminal-based visualiser for Limitless temporal fields.

    Usage
    -----
    >>> vis = FieldVisualiser(width=60)
    >>> vis.entropy_bars(nodes)
    >>> vis.trajectory_sparklines(nodes)
    >>> vis.influence_matrix(nodes)
    >>> vis.phase_portrait(nodes)
    """

    def __init__(self, width: int = 64, color: bool = True):
        self.width = width
        self.color = color

    # ── Entropy bar chart ─────────────────────────────────────────────────────

    def entropy_bars(self, nodes: List[TemporalNode], title: str = "Entropy Field") -> str:
        bar_width = self.width - 26
        lines = [self._header(title)]

        for node in nodes:
            s = node.current_state
            h_fill = int(s.entropy * bar_width)
            c_fill = int(s.coherence * bar_width)
            label = (node.label or node.id[:8])[:14].ljust(14)

            h_bar = self._colored(BLOCK * h_fill + LIGHT * (bar_width - h_fill), s.entropy)
            lines.append(f"  {label}  H:[{h_bar}] {s.entropy:.2f}  Ω:{s.omega():.3f}")

        lines.append(self._footer())
        return "\n".join(lines)

    # ── Trajectory sparklines ─────────────────────────────────────────────────

    def trajectory_sparklines(self, nodes: List[TemporalNode], title: str = "Entropy Trajectories") -> str:
        lines = [self._header(title)]
        spark_len = self.width - 22

        for node in nodes:
            label = (node.label or node.id[:8])[:14].ljust(14)
            series = [s.entropy for s in node.state_history[-spark_len:]] + [node.current_state.entropy]
            spark = self._sparkline(series, spark_len)
            current = node.current_state.entropy
            lines.append(f"  {label}  {spark}  {current:.3f}")

        lines.append(self._footer())
        return "\n".join(lines)

    # ── Influence matrix ──────────────────────────────────────────────────────

    def influence_matrix(self, nodes: List[TemporalNode], title: str = "Temporal Influence Matrix") -> str:
        n = len(nodes)
        if n == 0:
            return "(empty)"
        lines = [self._header(title)]

        # Header row
        labels = [(nd.label or nd.id[:4])[:4] for nd in nodes]
        header = "         " + "  ".join(f"{l:>4}" for l in labels)
        lines.append(header)
        lines.append("         " + "─" * (6 * n))

        for i, src in enumerate(nodes):
            row_label = labels[i].ljust(6)
            cells = []
            for j, tgt in enumerate(nodes):
                if i == j:
                    cells.append("  ██  ")
                else:
                    inf = src.field_influence(tgt)
                    intensity = min(1.0, inf / 10.0)   # normalise
                    block = self._intensity_char(intensity)
                    cells.append(f"  {block}{block}{block}  ")
            lines.append(f"  {row_label}" + "".join(cells))

        lines.append(self._footer())
        return "\n".join(lines)

    # ── Phase portrait (entropy × momentum) ──────────────────────────────────

    def phase_portrait(
        self,
        nodes: List[TemporalNode],
        title: str = "Phase Portrait  (H × momentum)",
        rows: int = 20,
        cols: int = 48,
    ) -> str:
        lines = [self._header(title)]
        grid = [[" "] * cols for _ in range(rows)]

        # Axes
        mid_row = rows // 2
        for c in range(cols):
            grid[mid_row][c] = "─"
        for r in range(rows):
            grid[r][0] = "│"
        grid[mid_row][0] = "┼"

        # Plot nodes
        for node in nodes:
            s = node.current_state
            col = int(s.entropy * (cols - 2)) + 1
            row = int((1.0 - (s.momentum + 1.0) / 2.0) * (rows - 1))
            row = max(0, min(rows - 1, row))
            col = max(1, min(cols - 1, col))
            marker = (node.label or "?")[0].upper()
            grid[row][col] = self._colored(marker, s.entropy)

        lines.append(f"  p↑")
        for row in grid:
            lines.append("  " + "".join(row))
        lines.append(f"  {'0':>2}{'─' * (cols // 2 - 2)}{'H →'}")
        lines.append(self._footer())
        return "\n".join(lines)

    # ── Full report ───────────────────────────────────────────────────────────

    def full_report(self, field: TemporalField) -> str:
        nodes = list(field.nodes.values())
        parts = [
            self.entropy_bars(nodes),
            self.trajectory_sparklines(nodes),
            self.phase_portrait(nodes),
        ]
        if len(nodes) <= 8:
            parts.append(self.influence_matrix(nodes))
        return "\n\n".join(parts)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _header(self, title: str) -> str:
        pad = max(0, self.width - len(title) - 4)
        return f"\n  ┌─ {title} {'─' * pad}┐"

    def _footer(self) -> str:
        return "  └" + "─" * (self.width - 2) + "┘"

    def _sparkline(self, series: List[float], length: int) -> str:
        if not series:
            return " " * length
        lo, hi = min(series), max(series)
        span = hi - lo or 1.0
        chars = []
        step = max(1, len(series) // length)
        sampled = series[::step][:length]
        for v in sampled:
            idx = int((v - lo) / span * (len(SPARKS) - 1))
            chars.append(SPARKS[idx])
        return ("".join(chars)).ljust(length)

    def _intensity_char(self, v: float) -> str:
        idx = min(len(FILL) - 1, int(v * len(FILL)))
        return FILL[idx]

    def _colored(self, text: str, intensity: float) -> str:
        if not self.color:
            return text
        # Blue → green → yellow → red gradient
        if intensity < 0.33:
            code = "\033[34m"   # blue
        elif intensity < 0.66:
            code = "\033[32m"   # green
        else:
            code = "\033[31m"   # red
        return f"{code}{text}\033[0m"
