"""Mathematical utilities for temporal analysis."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from ..core.node import TemporalNode


def omega_matrix(nodes: List[TemporalNode]) -> List[List[float]]:
    """
    Produce an N×N matrix of cross-node Ω influence scores.

    Entry [i][j] = influence node i exerts on node j.
    Diagonal entries are the node's self-Ω.
    """
    n = len(nodes)
    matrix = [[0.0] * n for _ in range(n)]
    for i, src in enumerate(nodes):
        for j, tgt in enumerate(nodes):
            if i == j:
                matrix[i][j] = src.current_state.omega()
            else:
                matrix[i][j] = src.field_influence(tgt)
    return matrix


def temporal_distance_matrix(nodes: List[TemporalNode]) -> List[List[float]]:
    """
    N×N symmetric matrix of temporal distances between all node pairs.
    """
    n = len(nodes)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = nodes[i].temporal_distance(nodes[j])
            matrix[i][j] = dist
            matrix[j][i] = dist
    return matrix


def entropy_gradient(nodes: List[TemporalNode]) -> float:
    """
    Standard deviation of entropy across nodes.
    High gradient → heterogeneous field (interesting structure forming).
    """
    if not nodes:
        return 0.0
    entropies = [n.current_state.entropy for n in nodes]
    mean = sum(entropies) / len(entropies)
    variance = sum((e - mean) ** 2 for e in entropies) / len(entropies)
    return math.sqrt(variance)


def normalize(values: List[float]) -> List[float]:
    """Min-max normalize a list of floats to [0, 1]."""
    lo, hi = min(values), max(values)
    span = hi - lo
    if span < 1e-9:
        return [0.5] * len(values)
    return [(v - lo) / span for v in values]


def weighted_average(values: List[float], weights: List[float]) -> float:
    """Weighted average of values."""
    total_w = sum(weights)
    if total_w < 1e-9:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_w


def sigmoid(x: float) -> float:
    """Standard logistic sigmoid."""
    return 1.0 / (1.0 + math.exp(-x))


def temporal_coherence_score(history: List[float]) -> float:
    """
    Measure how coherent (smooth) a temporal trajectory is.

    1.0 = perfectly smooth monotonic change.
    0.0 = completely erratic.
    """
    if len(history) < 2:
        return 1.0
    deltas = [abs(history[i] - history[i - 1]) for i in range(1, len(history))]
    mean_delta = sum(deltas) / len(deltas)
    # Variance of deltas: low variance = smooth
    var = sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)
    return max(0.0, 1.0 - min(1.0, var * 10))
