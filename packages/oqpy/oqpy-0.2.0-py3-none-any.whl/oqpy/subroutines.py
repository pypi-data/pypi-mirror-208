from __future__ import annotations
import functools
import inspect
from typing import Callable, get_type_hints, TYPE_CHECKING

from openqasm import ast

from oqpy.classical_types import (
    AstConvertible,
    OQFunctionCall,
    OQPyExpression,
    _Var,
    map_to_ast,
    to_ast,
)
from oqpy.quantum_types import Qubit, QubitArray

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = ["subroutine", "declare_extern"]


def subroutine(func):
    @functools.wraps(func)
    def wrapper(program, *args):
        name = func.__name__
        identifier = ast.Identifier(func.__name__)
        argnames = inspect.signature(func).parameters.keys()
        type_hints = get_type_hints(func)
        inputs = {}  # used as inputs when calling the actual python function
        arguments = []  # used in the ast definition of the subroutine
        for argname in argnames:
            if argname not in type_hints:
                raise ValueError(f"No type hint provided for {argname} on subroutine {name}")
            input_ = inputs[argname] = type_hints[argname](
                program, ident=argname, autodeclare=False
            )
            input_.set_captured()

            if isinstance(input_, _Var):
                arguments.append(ast.ClassicalArgument(input_.type, ast.Identifier(argname)))
            elif isinstance(input_, Qubit):
                arguments.append(ast.QuantumArgument(input_.ident, None))
            elif isinstance(input_, QubitArray):
                arguments.append(ast.QuantumArgument(input_.ident, ast.IntegerLiteral(input_.size)))
            else:
                raise ValueError(
                    f"Type hint for {argname} on subroutine {name} is not an oqpy variable type"
                )

        program.push()
        output = func(**inputs)
        state = program.pop()
        body = state.body
        if isinstance(output, OQPyExpression):
            return_type = output.type
            body.append(ast.ReturnStatement(to_ast(output)))
        elif output is None:
            return_type = None
        else:
            raise ValueError(
                "Output type of subroutine {name} was neither oqpy expression nor None"
            )
        stmt = ast.SubroutineDefinition(
            identifier,
            arguments=arguments,
            return_type=return_type,
            body=body,
        )

        program.add_subroutine(name, stmt)
        return OQFunctionCall(program, identifier, args, return_type)

    return wrapper


def declare_extern(program: Program, name: str, argtypes, return_type) -> Callable:
    extern_decl = ast.ExternDeclaration(
        ast.Identifier(name),
        argtypes,
        return_type,
    )

    def call_extern(*args: list[AstConvertible]):
        return OQFunctionCall(program, name, map_to_ast(args), return_type, extern_decl=extern_decl)

    return call_extern
