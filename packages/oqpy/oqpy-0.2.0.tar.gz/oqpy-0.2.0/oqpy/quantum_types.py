from __future__ import annotations
import contextlib
from typing import Union, TYPE_CHECKING

from openqasm import ast

from oqpy.classical_types import (
    AstConvertible,
    BitVar,
    convert_range,
    map_to_ast,
    to_ast,
)

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = ["Qubit", "gate", "QubitArray", "defcal"]


class Qubit:
    def __init__(
        self,
        program: Program,
        identifier: Union[str, ast.Identifier, ast.IndexIdentifier],
        autodeclare=True,
    ):
        self.program = program
        if isinstance(identifier, str):
            self.ident = ast.Identifier(identifier)
            if autodeclare:
                program.add_statement(ast.QubitDeclaration(self.ident, None))
        else:
            assert not autodeclare
            self.ident = identifier

    def define_measure(self):
        pass

    def measure(self, output_location: BitVar):
        self.program.add_statement(
            ast.QuantumMeasurementAssignment(self.ident, output_location.to_ast())
        )


class _PhysicalQubits:
    def __init__(self, program: Program):
        self.program = program

    def __getitem__(self, item: int) -> Qubit:
        return Qubit(self.program, ast.Identifier(f"${item}"), autodeclare=False)


def gate(program: Program, qubits: Union[Qubit, list[Qubit]], name: str, *args):
    if isinstance(qubits, Qubit):
        qubits = [qubits]
    program.add_statement(
        ast.QuantumGate(
            [],
            ast.Identifier(name),
            map_to_ast(args),
            [q.ident for q in qubits],
        )
    )


class QubitArray:
    def __init__(
        self,
        program: Program,
        identifier: Union[str, ast.Identifier, ast.IndexIdentifier],
        size: int,
        autodeclare=True,
    ):
        self.program = program
        self.size = size
        if isinstance(identifier, str):
            self.ident = ast.Identifier(identifier)
            if autodeclare:
                program.add_statement(ast.QubitDeclaration(self.ident, ast.IntegerLiteral(size)))
        else:
            assert not autodeclare
            self.ident = identifier

    def measure(self, output_location: BitVar):
        self.program.add_statement(
            ast.QuantumMeasurementAssignment(
                ast.QuantumMeasurement(self.ident),
                output_location.to_ast(),
            )
        )

    def __getitem__(self, item):
        name = self.ident.name
        if isinstance(item, (list, tuple)):
            return QubitArray(ast.Selection(name, map_to_ast(item)), len(item), autodeclare=False)
        if isinstance(item, slice):
            return QubitArray(
                ast.Slice(name, convert_range(item)), item.stop - item.start, autodeclare=False
            )
        if isinstance(item, AstConvertible.__args__):
            return Qubit(ast.Subscript(name, to_ast(item)), autodeclare=False)
        raise TypeError


@contextlib.contextmanager
def defcal(program: Program, qubits: Union[Qubit, list[Qubit]], name: str):
    program.push()
    yield
    state = program.pop()

    if isinstance(qubits, Qubit):
        qubits = [qubits]

    program.add_statement(
        ast.CalibrationDefinition(
            ast.Identifier(name),
            [],  # todo: support arguments
            [q.ident for q in qubits],
            None,  # todo: support return type,
            state.body,
        )
    )
