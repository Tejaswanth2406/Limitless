"""
Structured logger for the Limitless framework.

Provides a consistent logging interface with:
- Severity levels: DEBUG, INFO, WARN, ERROR, CRITICAL
- Optional timestamps
- Module-scoped loggers
- File sink support
"""

from __future__ import annotations

import sys
import time
from enum import IntEnum
from typing import Optional, TextIO


class Level(IntEnum):
    DEBUG    = 10
    INFO     = 20
    WARN     = 30
    ERROR    = 40
    CRITICAL = 50


_LABELS = {
    Level.DEBUG:    "DBG",
    Level.INFO:     "INF",
    Level.WARN:     "WRN",
    Level.ERROR:    "ERR",
    Level.CRITICAL: "CRT",
}

_COLORS = {
    Level.DEBUG:    "\033[36m",    # cyan
    Level.INFO:     "\033[32m",    # green
    Level.WARN:     "\033[33m",    # yellow
    Level.ERROR:    "\033[31m",    # red
    Level.CRITICAL: "\033[35m",    # magenta
}
_RESET = "\033[0m"


class LimitlessLogger:
    """
    Lightweight structured logger.

    Usage
    -----
    >>> log = get_logger("core.kernel")
    >>> log.info("Kernel started")
    >>> log.warn("High entropy detected", node="market", entropy=0.89)
    """

    def __init__(
        self,
        name: str,
        level: Level = Level.INFO,
        sink: Optional[TextIO] = None,
        use_color: bool = True,
        timestamps: bool = True,
    ):
        self.name = name
        self.level = level
        self.sink = sink or sys.stderr
        self.use_color = use_color
        self.timestamps = timestamps
        self._entries: list = []

    # ── Logging methods ────────────────────────────────────────────────────────

    def debug(self, msg: str, **ctx) -> None:
        self._log(Level.DEBUG, msg, ctx)

    def info(self, msg: str, **ctx) -> None:
        self._log(Level.INFO, msg, ctx)

    def warn(self, msg: str, **ctx) -> None:
        self._log(Level.WARN, msg, ctx)

    def error(self, msg: str, **ctx) -> None:
        self._log(Level.ERROR, msg, ctx)

    def critical(self, msg: str, **ctx) -> None:
        self._log(Level.CRITICAL, msg, ctx)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _log(self, lvl: Level, msg: str, ctx: dict) -> None:
        if lvl < self.level:
            return

        ts = f"{time.strftime('%H:%M:%S')} " if self.timestamps else ""
        label = _LABELS[lvl]
        color = _COLORS[lvl] if self.use_color else ""
        reset = _RESET if self.use_color else ""

        ctx_str = ""
        if ctx:
            ctx_str = "  " + "  ".join(f"{k}={v}" for k, v in ctx.items())

        line = f"{color}{ts}[{label}] {self.name}: {msg}{ctx_str}{reset}"
        self.sink.write(line + "\n")
        self.sink.flush()

        self._entries.append({
            "time": time.time(),
            "level": lvl.name,
            "name": self.name,
            "msg": msg,
            "ctx": ctx,
        })

    def history(self, min_level: Level = Level.DEBUG) -> list:
        return [e for e in self._entries if Level[e["level"]] >= min_level]

    def set_level(self, level: Level) -> None:
        self.level = level


# ── Registry ──────────────────────────────────────────────────────────────────

_registry: dict[str, LimitlessLogger] = {}


def get_logger(
    name: str,
    level: Level = Level.INFO,
    use_color: bool = True,
) -> LimitlessLogger:
    """Get or create a named logger."""
    if name not in _registry:
        _registry[name] = LimitlessLogger(name=name, level=level, use_color=use_color)
    return _registry[name]


def set_global_level(level: Level) -> None:
    """Set the log level for all registered loggers."""
    for logger in _registry.values():
        logger.set_level(level)
