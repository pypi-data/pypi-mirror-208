from __future__ import annotations

from copy import deepcopy
from typing import Optional, TYPE_CHECKING

from openqasm import ast
from openqasm.printer import print_qasm
from oqpy import pulse
from oqpy import timing
from oqpy import quantum_types

if TYPE_CHECKING:
    from oqpy import AstConvertible


__all__ = ["Program"]


class ProgramState:
    def __init__(self):
        self.body: list[ast.Statement] = []
        self.if_clause: Optional[ast.BranchingStatement] = None

    def add_if_clause(self, condition: ast.Expression, if_clause: list[ast.Statement]):
        self.finalize_if_clause()
        self.if_clause = ast.BranchingStatement(condition, if_clause, [])

    def add_else_clause(self, else_clause: list[ast.Statement]):
        if self.if_clause is None:
            raise RuntimeError("Else without If.")
        self.if_clause.else_block = else_clause
        self.finalize_if_clause()

    def finalize_if_clause(self):
        if self.if_clause is not None:
            if_clause, self.if_clause = self.if_clause, None
            self.add_statement(if_clause)

    def add_statement(self, stmt: ast.Statement):
        self.finalize_if_clause()
        self.body.append(stmt)


class Program:
    def __init__(self):
        self.stack: list[ProgramState] = [ProgramState()]
        self.defcals: dict[tuple[str, str], ast.CalibrationDefinition] = {}
        self.subroutines: dict[str, ast.SubroutineDefinition] = {}
        self.externs: dict[str, ast.ExternDeclaration] = {}
        self.physical_qubits = quantum_types._PhysicalQubits(self)

    def __iadd__(self, other):
        if len(other.stack) > 1:
            raise RuntimeError("Cannot add subprogram with unclosed contextmanagers")
        self.state.finalize_if_clause()
        self.state.body.extend(other.state.body)
        self.state.if_clause = other.state.if_clause
        self.state.finalize_if_clause()
        self.defcals.update(other.defcals)
        self.subroutines.update(other.subroutines)
        self.externs.update(other.externs)
        return self

    def __add__(self, other):
        self_copy = deepcopy(self)
        self_copy += other
        return self_copy

    @property
    def state(self) -> ProgramState:
        return self.stack[-1]

    def push(self):
        self.stack.append(ProgramState())

    def pop(self) -> ProgramState:
        state = self.stack.pop()
        state.finalize_if_clause()
        return state

    def add_statement(self, stmt):
        self.state.add_statement(stmt)

    def add_subroutine(self, name: str, stmt: ast.SubroutineDefinition):
        self.subroutines[name] = stmt

    def add_defcal(self, qubit_name: str, name: str, stmt: ast.CalibrationDefinition):
        self.defcals[(qubit_name, name)] = stmt

    def to_ast(self, encal=False, include_externs=True) -> ast.Program:
        assert len(self.stack) == 1
        self.state.finalize_if_clause()
        statements = []
        if include_externs:
            statements += list(self.externs.values())
        statements += list(self.subroutines.values()) + self.state.body
        if encal:
            statements = [ast.CalibrationBlock(statements)]
        return ast.Program(statements=statements)

    def to_qasm(self, encal=False, include_externs=True) -> str:
        return print_qasm(
            self.to_ast(encal=encal, include_externs=include_externs), pretty_print=True
        )

    def delay(self, time, qubits=()):
        timing.delay(self, time, qubits)
        return self

    def barrier(self, qubits):
        timing.barrier(self, qubits)
        return self

    def play(self, frame: pulse.Frame, waveform: AstConvertible):
        frame.play(waveform)
        return self

    def capture(self, frame: pulse.Frame, kernel: AstConvertible):
        frame.capture(kernel)
        return self

    def set_phase(self, frame: pulse.Frame, phase: AstConvertible):
        frame.set_phase(phase)
        return self

    def shift_phase(self, frame: pulse.Frame, phase: AstConvertible):
        frame.shift_phase(phase)
        return self

    def set_frequency(self, frame: pulse.Frame, freq: AstConvertible):
        frame.set_frequency(freq)
        return self

    def shift_frequency(self, frame: pulse.Frame, freq: AstConvertible):
        frame.shift_frequency(freq)
        return self

    def set_scale(self, frame: pulse.Frame, scale: AstConvertible):
        frame.set_scale(scale)
        return self

    def shift_scale(self, frame: pulse.Frame, scale: AstConvertible):
        frame.shift_scale(scale)
        return self

    def gate(self, qubits, name):
        quantum_types.gate(self, qubits, name)
        return self
