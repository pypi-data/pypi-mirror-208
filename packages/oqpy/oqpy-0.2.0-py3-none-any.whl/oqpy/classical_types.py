from __future__ import annotations
import functools
import random
import string
from typing import Optional, Type, Union, final, TYPE_CHECKING

from openqasm import ast

if TYPE_CHECKING:
    from oqpy.program import Program


__all__ = [
    "AstConvertible",
    "IntVar",
    "FloatVar",
    "BitVar",
    "ComplexVar",
    "DurationVar",
    "Stretch",
]


class OQPyExpression:
    def __init__(self, program: Program):
        self.program = program
        self.captured = False

    def type(self):
        raise NotImplementedError

    def set_captured(self):
        self.captured = True

    @final
    def to_ast(self):
        self.set_captured()
        return self._to_ast()

    def _to_ast(self) -> ast.Expression:
        raise NotImplementedError

    def to_binary(self, op_name: str, first, second) -> OQPyBinaryExpression:
        return OQPyBinaryExpression(self.program, ast.BinaryOperator[op_name], first, second)

    def __add__(self, other):
        return self.to_binary("+", self, other)

    def __radd__(self, other):
        return self.to_binary("+", other, self)

    def __mod__(self, other):
        return self.to_binary("%", self, other)

    def __rmod__(self, other):
        return self.to_binary("%", other, self)

    def __mul__(self, other):
        return self.to_binary("*", self, other)

    def __rmul__(self, other):
        return self.to_binary("*", other, self)

    def __eq__(self, other):
        return self.to_binary("==", self, other)

    def __ne__(self, other):
        return self.to_binary("!=", self, other)

    def __gt__(self, other):
        return self.to_binary(">", self, other)

    def __lt__(self, other):
        return self.to_binary("<", self, other)

    def __ge__(self, other):
        return self.to_binary(">=", self, other)

    def __le__(self, other):
        return self.to_binary("<=", self, other)

    def __del__(self):
        if not self.captured:
            self.program.add_statement(ast.ExpressionStatement(self.to_ast()))


AstConvertible = Union[OQPyExpression, int, float, ast.Expression]


def convert_range(item: Union[slice, range]) -> ast.RangeDefinition:
    return ast.RangeDefinition(to_ast(item.start), to_ast(item.stop - 1), to_ast(item.step))


def to_ast(item: AstConvertible) -> ast.Expression:
    if isinstance(item, int):
        return ast.IntegerLiteral(item)
    if isinstance(item, float):
        return ast.RealLiteral(item)
    if isinstance(item, OQPyExpression):
        return item.to_ast()
    if isinstance(item, ast.Expression):
        return item
    raise TypeError(f"Cannot convert {item} of type {type(item)} to ast")


def optional_ast(item: Optional[AstConvertible]) -> Optional[ast.Expression]:
    if item is None:
        return None
    return to_ast(item)


def map_to_ast(items: list[AstConvertible]) -> list[ast.Expression]:
    return list(map(to_ast, items))


class OQPyBinaryExpression(OQPyExpression):
    def __init__(
        self, program: Program, op: ast.BinaryOperator, lhs: AstConvertible, rhs: AstConvertible
    ):
        super().__init__(program)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        # TODO: Fix this!
        if isinstance(lhs, OQPyExpression):
            self.type = lhs.type
        elif isinstance(rhs, OQPyExpression):
            self.type = rhs.type
        else:
            raise TypeError("Neither lhs nor rhs is an expression?")

    def _to_ast(self) -> ast.Expression:
        return ast.BinaryExpression(self.op, to_ast(self.lhs), to_ast(self.rhs))


def make_identifier_name() -> str:
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


class _Var(OQPyExpression):
    type_cls: Type[ast.ClassicalType]

    def __init__(
        self,
        program: Program,
        init_expression=None,
        ident: Optional[str] = None,
        autodeclare=True,
        **type_kwargs,
    ):
        super().__init__(program)
        self.ident = ast.Identifier(ident or make_identifier_name())
        self.type = self.type_cls(**type_kwargs)
        init_expression = optional_ast(init_expression)
        if autodeclare:
            self.set_captured()
            self.program.add_statement(
                ast.ClassicalDeclaration(self.type, self.ident, init_expression)
            )

    def _to_ast(self) -> ast.Identifier:
        return self.ident

    def _do_assignment(self, other, op: ast.AssignmentOperator):
        self.program.add_statement(ast.ClassicalAssignment(self.to_ast(), op, to_ast(other)))

    def set(self, other):
        self._do_assignment(other, ast.AssignmentOperator["="])

    def __iadd__(self, other):
        self._do_assignment(other, ast.AssignmentOperator["+="])
        return self

    def __isub__(self, other):
        self._do_assignment(other, ast.AssignmentOperator["-="])
        return self

    # def __getitem__(self, item: int):
    #     return VarSlice(self, item)


class _SizedVar(_Var):
    default_size = None

    def __class_getitem__(cls, item: int):
        return functools.partial(cls, size=item)

    def __init__(self, *args, size=None, **kwargs):
        if size is None:
            size = self.default_size
        if size is not None:
            size = to_ast(size)
        super().__init__(*args, **kwargs, size=size)


class IntVar(_SizedVar):
    type_cls = ast.IntType
    default_size = 32

    def __imod__(self, other):
        self._do_assignment(other, ast.AssignmentOperator["%="])


class FloatVar(_SizedVar):
    type_cls = ast.FloatType
    default_size = 64


class BitVar(_SizedVar):
    type_cls = ast.BitType


class ComplexVar(_Var):
    type_cls = ast.ComplexType

    def __class_getitem__(cls, item):
        return functools.partial(cls, base_type=item)

    def __init__(self, program: Program, *args, base_type=FloatVar, **kwargs):
        base_type_instance = base_type(program, autodeclare=False)
        base_type_instance.set_captured()
        super().__init__(program, *args, **kwargs, base_type=base_type_instance.type)


def make_duration(time) -> ast.Expression:
    if isinstance(time, float):
        # Todo: make better units?
        return ast.DurationLiteral(1e9 * time, ast.TimeUnit.ns)
    elif isinstance(time, OQPyExpression):
        return to_ast(time)


class DurationVar(_Var):
    type_cls = ast.DurationType

    def __init__(
        self,
        program: Program,
        init_expression=None,
        identifier: str = None,
        autodeclare=True,
        **type_kwargs,
    ):
        if init_expression is not None:
            init_expression = make_duration(init_expression)
        super().__init__(program, init_expression, identifier, autodeclare, **type_kwargs)


class Stretch(_Var):
    type_cls = ast.StretchType


class OQFunctionCall(OQPyExpression):
    def __init__(
        self,
        program: Program,
        identifier: Union[str, ast.Identifier],
        args,
        return_type,
        extern_decl=None,
    ):
        super().__init__(program)
        if isinstance(identifier, str):
            identifier = ast.Identifier(identifier)
        self.identifier = identifier
        self.args = args
        self.type = return_type
        self.extern_decl = extern_decl

    def _to_ast(self):
        if self.extern_decl is not None:
            self.program.externs[self.identifier.name] = self.extern_decl
        return ast.FunctionCall(self.identifier, map_to_ast(self.args))
