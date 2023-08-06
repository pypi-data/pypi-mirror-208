from __future__ import annotations
import contextlib
from typing import Optional, TYPE_CHECKING

from openqasm import ast

from oqpy.classical_types import IntVar, OQPyExpression, convert_range, map_to_ast, to_ast

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = ["If", "Else", "ForIn", "While"]


@contextlib.contextmanager
def If(program: Program, condition: OQPyExpression):
    program.push()
    yield
    state = program.pop()
    program.state.add_if_clause(to_ast(condition), state.body)


@contextlib.contextmanager
def Else(program: Program):
    program.push()
    yield
    state = program.pop()
    program.state.add_else_clause(state.body)


@contextlib.contextmanager
def ForIn(program: Program, iterator, identifier: Optional[str] = None):
    program.push()
    var = IntVar(program, ident=identifier, autodeclare=False)
    var.set_captured()
    yield var
    state = program.pop()

    if isinstance(iterator, list):
        iterator = map_to_ast(iterator)
    elif isinstance(iterator, range):
        iterator = convert_range(iterator)
    else:
        iterator = to_ast(iterator)

    stmt = ast.ForInLoop(var.ident, iterator, state.body)
    program.add_statement(stmt)


@contextlib.contextmanager
def While(program: Program, condition: OQPyExpression):
    program.push()
    yield
    state = program.pop()
    program.add_statement(ast.WhileLoop(to_ast(condition), state.body))
