"""Shared benchmark enums for Shadow Seed Learning."""

from __future__ import annotations

from enum import Enum


class RunType(str, Enum):
    SCAN = "benchmarkscan"
    PREPARATION = "benchmarkvoorbereiding"
    LIVE = "echte benchmarkrun"


class ExecutionStatus(str, Enum):
    SCAN = "benchmarkscan"
    PREPARATION = "benchmarkvoorbereiding"
    EXECUTION_GAP = "execution-gap aanwezig"
    LIVE = "echte benchmarkrun"


class HostStatus(str, Enum):
    UNVERIFIED = "te verifiëren"
    PRESENT = "aanwezig"
    VERIFIED = "geverifieerd"
    OUTDATED = "outdated"


class RunnerStatus(str, Enum):
    UNVERIFIED = "te verifiëren"
    STRUCTURE_PRESENT = "runnerstructuur aanwezig"
    VERIFIED = "geverifieerd"
    OUTDATED = "outdated"
    BLOCKED = "geblokkeerd"
