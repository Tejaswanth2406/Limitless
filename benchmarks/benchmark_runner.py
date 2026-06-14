"""
BenchmarkRunner — orchestrates and reports on multiple benchmark suites.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class BenchmarkResult:
    name: str
    passed: bool
    duration_seconds: float
    score: float            # 0–1, higher is better
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def __repr__(self) -> str:
        return (
            f"[{self.status()}] {self.name:<40} "
            f"score={self.score:.4f}  t={self.duration_seconds:.3f}s"
        )


class BaseBenchmark:
    """Abstract base for all benchmarks."""

    name: str = "unnamed"

    def run(self) -> BenchmarkResult:
        t0 = time.time()
        try:
            score, details = self._execute()
            passed = score >= self.passing_threshold()
            return BenchmarkResult(
                name=self.name,
                passed=passed,
                duration_seconds=time.time() - t0,
                score=score,
                details=details,
            )
        except Exception as exc:
            return BenchmarkResult(
                name=self.name,
                passed=False,
                duration_seconds=time.time() - t0,
                score=0.0,
                error=str(exc),
            )

    def _execute(self):
        raise NotImplementedError

    def passing_threshold(self) -> float:
        return 0.7


class BenchmarkRunner:
    """
    Runs a collection of benchmarks and produces a summary report.

    Usage
    -----
    >>> from Limitless.benchmarks import BenchmarkRunner, BenchmarkOmegaConvergence
    >>> runner = BenchmarkRunner()
    >>> runner.add(BenchmarkOmegaConvergence())
    >>> report = runner.run_all()
    >>> runner.print_report(report)
    """

    def __init__(self):
        self._benchmarks: List[BaseBenchmark] = []
        self._results: List[BenchmarkResult] = []

    def add(self, benchmark: BaseBenchmark) -> "BenchmarkRunner":
        self._benchmarks.append(benchmark)
        return self

    def add_all(self, benchmarks: List[BaseBenchmark]) -> "BenchmarkRunner":
        self._benchmarks.extend(benchmarks)
        return self

    def run_all(self) -> List[BenchmarkResult]:
        self._results = []
        for bench in self._benchmarks:
            result = bench.run()
            self._results.append(result)
        return self._results

    def print_report(self, results: Optional[List[BenchmarkResult]] = None) -> None:
        results = results or self._results
        sep = "=" * 70
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        avg_score = sum(r.score for r in results) / max(1, total)

        print(sep)
        print(f"  LIMITLESS BENCHMARK REPORT")
        print(sep)
        print(f"  Benchmarks : {total}")
        print(f"  Passed     : {passed}/{total}")
        print(f"  Avg Score  : {avg_score:.4f}")
        print(sep)
        for r in results:
            print(f"  {r}")
            if r.error:
                print(f"    ERROR: {r.error}")
            if r.details:
                for k, v in list(r.details.items())[:3]:
                    print(f"    {k}: {v}")
        print(sep)

    def summary_dict(self) -> Dict[str, Any]:
        results = self._results
        return {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "avg_score": sum(r.score for r in results) / max(1, len(results)),
            "results": [
                {"name": r.name, "passed": r.passed, "score": r.score}
                for r in results
            ],
        }
