"""Shared benchmark enums for Shadow Seed Learning."""

from __future__ import annotations

from enum import Enum


class RunType(str, Enum):
    SCAN = "benchmarkscan"
    PREPARATION = "benchmarkvoorbereiding"
    LIVE = "echte benchmarkrun"


class ExecutionStatus(str, Enum):
    PREPARATION = "benchmarkvoorbereiding"
    EXECUTION_GAP = "execution-gap aanwezig"
    LIVE = "echte benchmarkrun"
