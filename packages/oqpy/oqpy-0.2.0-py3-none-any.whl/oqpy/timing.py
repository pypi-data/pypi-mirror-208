from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING

from openqasm import ast

from oqpy.classical_types import make_duration

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = ["barrier", "delay", "Box"]


def barrier(program: Program, qubits=()):
    program.add_statement(ast.QuantumBarrier([q.ident for q in qubits]))


def delay(program: Program, time, qubits=()):
    program.add_statement(ast.DelayInstruction([], make_duration(time), [q.ident for q in qubits]))


@contextlib.contextmanager
def Box(program: Program, duration=None):
    if duration is not None:
        duration = make_duration(duration)
    program.push()
    yield
    state = program.pop()
    program.add_statement(ast.Box(duration, state.body))
