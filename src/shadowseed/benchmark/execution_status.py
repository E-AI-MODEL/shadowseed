"""Execution status logic for SSL benchmark lanes."""

from __future__ import annotations

from dataclasses import dataclass, field

from .run_types import ExecutionStatus, HostStatus, RunType, RunnerStatus


@dataclass
class ExecutionDecision:
    run_type: str
    execution_status: str
    execution_gap: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_type": self.run_type,
            "execution_status": self.execution_status,
            "execution_gap": self.execution_gap,
            "notes": self.notes,
        }



def resolve_execution_status(
    requested_run_type: str,
    host_status: str,
    runner_status: str,
    execution_gap: bool,
) -> ExecutionDecision:
    notes: list[str] = []

    if host_status == HostStatus.OUTDATED.value or runner_status == RunnerStatus.OUTDATED.value:
        notes.append("outdated repo of host blokkeert echte benchmarkrun")
        return ExecutionDecision(
            run_type=RunType.PREPARATION.value,
            execution_status=ExecutionStatus.EXECUTION_GAP.value,
            execution_gap=True,
            notes=notes,
        )

    if runner_status == RunnerStatus.BLOCKED.value:
        notes.append("runner is expliciet geblokkeerd")
        return ExecutionDecision(
            run_type=RunType.PREPARATION.value,
            execution_status=ExecutionStatus.EXECUTION_GAP.value,
            execution_gap=True,
            notes=notes,
        )

    if requested_run_type == RunType.LIVE.value:
        if (
            host_status == HostStatus.VERIFIED.value
            and runner_status == RunnerStatus.VERIFIED.value
            and not execution_gap
        ):
            notes.append("host en runner zijn hard genoeg geverifieerd voor live route")
            return ExecutionDecision(
                run_type=RunType.LIVE.value,
                execution_status=ExecutionStatus.LIVE.value,
                execution_gap=False,
                notes=notes,
            )

        notes.append("live route is aangevraagd maar nog niet hard genoeg geverifieerd")
        return ExecutionDecision(
            run_type=RunType.PREPARATION.value,
            execution_status=ExecutionStatus.EXECUTION_GAP.value,
            execution_gap=True,
            notes=notes,
        )

    if requested_run_type == RunType.SCAN.value:
        notes.append("benchmarkscan blijft toegestaan zolang host of runner niet live-klaar zijn")
        return ExecutionDecision(
            run_type=RunType.SCAN.value,
            execution_status=ExecutionStatus.SCAN.value,
            execution_gap=execution_gap,
            notes=notes,
        )

    notes.append("benchmarkvoorbereiding blijft de eerlijke standaardstatus")
    if execution_gap:
        notes.append("execution-gap blijft aanwezig")
    return ExecutionDecision(
        run_type=RunType.PREPARATION.value,
        execution_status=(
            ExecutionStatus.EXECUTION_GAP.value
            if execution_gap
            else ExecutionStatus.PREPARATION.value
        ),
        execution_gap=execution_gap,
        notes=notes,
    )
