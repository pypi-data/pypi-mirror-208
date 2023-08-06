from __future__ import annotations
import contextlib
from typing import Optional, TYPE_CHECKING

from openqasm import ast

from oqpy.classical_types import AstConvertible, OQFunctionCall, _Var
from oqpy.subroutines import declare_extern

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = ["PortVar", "WaveformVar", "Frame", "constant_waveform", "gaussian_waveform", "Cal"]


class PortVar(_Var):
    type_cls = ast.PulseType

    def __init__(self, program: Program, ident=None, **kwargs):
        super().__init__(program, ident=ident, **kwargs, type=ast.PulseTypeName.port)


class WaveformVar(_Var):
    type_cls = ast.PulseType

    def __init__(self, program: Program, init_expression=None, ident=None, **kwargs):
        super().__init__(
            program,
            init_expression=init_expression,
            ident=ident,
            **kwargs,
            type=ast.PulseTypeName.waveform,
        )


class Frame(_Var):
    type_cls = ast.PulseType

    def __init__(
        self,
        program: Program = None,
        port: Optional[PortVar] = None,
        frequency: AstConvertible = None,
        phase: AstConvertible = 0,
        ident=None,
        autodeclare=True,
    ):
        if port is None != frequency is None:
            raise ValueError("Must declare both port and frequency or neither")
        init_expression = port and OQFunctionCall(
            program, "newframe", [port, frequency, phase], ast.PulseType(ast.PulseTypeName.frame)
        )
        super().__init__(
            program, init_expression, ident, autodeclare=autodeclare, type=ast.PulseTypeName.frame
        )

    def _resolve_program(self, program: Program | None) -> Program:
        if program is not None:
            return program
        if self.program is None

    def play(self, waveform: AstConvertible, program):
        self.set_captured()
        program = self._resolve_program
        return OQFunctionCall(self.program, "play", [waveform, self.ident], None)

    def capture(self, kernel: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "capture", [kernel, self.ident], None)

    def set_phase(self, phase: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "set_phase", [phase, self.ident], None)

    def shift_phase(self, phase: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "shift_phase", [phase, self.ident], None)

    def set_frequency(self, freq: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "set_frequency", [freq, self.ident], None)

    def shift_frequency(self, freq: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "shift_frequency", [freq, self.ident], None)

    def set_scale(self, scale: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "set_scale", [scale, self.ident], None)

    def shift_scale(self, scale: AstConvertible):
        self.set_captured()
        return OQFunctionCall(self.program, "shift_scale", [scale, self.ident], None)


def _make_waveform(program: Program, name: str, argtypes, args):
    func = declare_extern(program, name, argtypes, ast.PulseType(ast.PulseTypeName.waveform))
    return func(*args)


def constant_waveform(program: Program, length: float, amp: float):
    return _make_waveform(
        program,
        "constant",
        [ast.DurationType(), ast.FloatType(ast.IntegerLiteral(64))],
        [length, amp],
    )


def gaussian_waveform(
    program: Program, length: float, sigma: float, amp: float, phase: float = 0.0
):
    return _make_waveform(
        program,
        "gaussian",
        [
            ast.DurationType(),
            ast.DurationType(),
            ast.FloatType(ast.IntegerLiteral(64)),
            ast.FloatType(ast.IntegerLiteral(64)),
        ],
        [length, sigma, amp, phase],
    )


@contextlib.contextmanager
def Cal(program):
    """Context manager that begins a cal block."""
    program.push()
    yield
    state = program.pop()
    program.add_statement(ast.CalibrationBlock(state.body))
