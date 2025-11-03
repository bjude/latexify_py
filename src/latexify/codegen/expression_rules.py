"""Codegen rules for single expressions."""

from __future__ import annotations

import ast
import dataclasses

# Precedences of operators for BoolOp, BinOp, UnaryOp, and Compare nodes.
# Note that this value affects only the appearance of surrounding parentheses for each
# expression, and does not affect the AST itself.
# See also:
# https://docs.python.org/3/reference/expressions.html#operator-precedence
_PRECEDENCES: dict[type[ast.AST], int] = {
    ast.Pow: 120,
    ast.UAdd: 110,
    ast.USub: 110,
    ast.Invert: 110,
    ast.Mult: 100,
    ast.MatMult: 100,
    ast.Div: 100,
    ast.FloorDiv: 100,
    ast.Mod: 100,
    ast.Add: 90,
    ast.Sub: 90,
    ast.LShift: 80,
    ast.RShift: 80,
    ast.BitAnd: 70,
    ast.BitXor: 60,
    ast.BitOr: 50,
    ast.In: 40,
    ast.NotIn: 40,
    ast.Is: 40,
    ast.IsNot: 40,
    ast.Lt: 40,
    ast.LtE: 40,
    ast.Gt: 40,
    ast.GtE: 40,
    ast.NotEq: 40,
    ast.Eq: 40,
    # NOTE(odashi):
    # We assume that the `not` operator has the same precedence with other unary
    # operators `+`, `-` and `~`, because the LaTeX counterpart $\lnot$ looks to have a
    # high precedence.
    # ast.Not: 30,
    ast.Not: 110,
    ast.And: 20,
    ast.Or: 10,
}

# NOTE(odashi):
# Function invocation is treated as a unary operator with a higher precedence.
# This ensures that the argument with a unary operator is wrapped:
#     exp(x) --> \exp x
#     exp(-x) --> \exp (-x)
#     -exp(x) --> - \exp x
_CALL_PRECEDENCE = _PRECEDENCES[ast.UAdd] + 1

_INF_PRECEDENCE = 1_000_000


def get_precedence(node: ast.AST) -> int:
    """Obtains the precedence of the subtree.

    Args:
        node: Subtree to investigate.

    Returns:
        If `node` is a subtree with some operator, returns the precedence of the
        operator. Otherwise, returns a number larger enough from other precedences.
    """
    if isinstance(node, ast.Call):
        return _CALL_PRECEDENCE

    if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
        return _PRECEDENCES[type(node.op)]

    if isinstance(node, ast.Compare):
        # Compare operators have the same precedence. It is enough to check only the
        # first operator.
        return _PRECEDENCES[type(node.ops[0])]

    return _INF_PRECEDENCE


@dataclasses.dataclass(frozen=True)
class BinOperandRule:
    """Syntax rules for operands of BinOp."""

    # Whether to require wrapping operands by parentheses according to the precedence.
    wrap: bool = True

    # Whether to require wrapping operands by parentheses if the operand has the same
    # precedence with this operator.
    # This is used to control the behavior of non-associative operators.
    force: bool = False


@dataclasses.dataclass(frozen=True)
class BinOpRule:
    """Syntax rules for BinOp."""

    # Left/middle/right syntaxes to wrap operands.
    latex_left: str
    latex_middle: str
    latex_right: str

    # Operand rules.
    operand_left: BinOperandRule = dataclasses.field(default_factory=BinOperandRule)
    operand_right: BinOperandRule = dataclasses.field(default_factory=BinOperandRule)

    # Whether to assume the resulting syntax is wrapped by some bracket operators.
    # If True, the parent operator can avoid wrapping this operator by parentheses.
    is_wrapped: bool = False


BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    ast.Pow: BinOpRule(
        "",
        "^(",
        ")",
        operand_left=BinOperandRule(force=True),
        operand_right=BinOperandRule(wrap=False),
    ),
    ast.Mult: BinOpRule("", " dot.op ", ""),
    ast.MatMult: BinOpRule("", " dot.op ", ""),
    ast.Div: BinOpRule(
        "frac(",
        ", ",
        ")",
        operand_left=BinOperandRule(wrap=False),
        operand_right=BinOperandRule(wrap=False),
    ),
    ast.FloorDiv: BinOpRule(
        "floor(frac(",
        ", ",
        "))",
        operand_left=BinOperandRule(wrap=False),
        operand_right=BinOperandRule(wrap=False),
        is_wrapped=True,
    ),
    ast.Mod: BinOpRule("", " op(%) ", "", operand_right=BinOperandRule(force=True)),
    ast.Add: BinOpRule("", " + ", ""),
    ast.Sub: BinOpRule("", " - ", "", operand_right=BinOperandRule(force=True)),
    ast.LShift: BinOpRule("", " << ", "", operand_right=BinOperandRule(force=True)),
    ast.RShift: BinOpRule("", " >> ", "", operand_right=BinOperandRule(force=True)),
    ast.BitAnd: BinOpRule("", " op(&) ", ""),
    ast.BitXor: BinOpRule("", " plus.o ", ""),
    ast.BitOr: BinOpRule("", " op(|) ", ""),
}

# Typeset for BinOp of sets.
SET_BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    **BIN_OP_RULES,
    ast.Sub: BinOpRule("", " without ", "", operand_right=BinOperandRule(force=True)),
    ast.BitAnd: BinOpRule("", " inter ", ""),
    ast.BitXor: BinOpRule("", " triangle ", ""),
    ast.BitOr: BinOpRule("", " union ", ""),
}

UNARY_OPS: dict[type[ast.unaryop], str] = {
    ast.Invert: "~",
    ast.UAdd: "+",  # Explicitly adds the $+$ operator.
    ast.USub: "-",
    ast.Not: "not ",
}

COMPARE_OPS: dict[type[ast.cmpop], str] = {
    ast.Eq: "=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.In: "in",
    ast.Is: "equiv",
    ast.IsNot: "equiv.not",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.NotEq: "eq.not",
    ast.NotIn: "in.not",
}

# Typeset for Compare of sets.
SET_COMPARE_OPS: dict[type[ast.cmpop], str] = {
    **COMPARE_OPS,
    ast.Gt: "supset",
    ast.GtE: "supset.eq",
    ast.Lt: "subset",
    ast.LtE: "subset.eq",
}

BOOL_OPS: dict[type[ast.boolop], str] = {
    ast.And: "and",
    ast.Or: "or",
}


@dataclasses.dataclass(frozen=True)
class FunctionRule:
    """Codegen rules for functions.

    Attributes:
        left: LaTeX expression concatenated to the left-hand side of the arguments.
        right: LaTeX expression concatenated to the right-hand side of the arguments.
        is_unary: Whether the function is treated as a unary operator or not.
        is_wrapped: Whether the resulting syntax is wrapped by brackets or not.
    """

    left: str
    right: str = ""
    is_unary: bool = False
    is_wrapped: bool = False


# name => left_syntax, right_syntax, is_wrapped
BUILTIN_FUNCS: dict[str, FunctionRule] = {
    "abs": FunctionRule("abs(", ")", is_wrapped=True),
    "acos": FunctionRule("arccos", is_unary=True),
    "acosh": FunctionRule('op("arcosh")', is_unary=True),
    "arccos": FunctionRule("arccos", is_unary=True),
    "arccot": FunctionRule('op("arccot")', is_unary=True),
    "arccsc": FunctionRule('op("arccsc")', is_unary=True),
    "arcosh": FunctionRule('op("arcosh")', is_unary=True),
    "arcoth": FunctionRule('op("arcoth")', is_unary=True),
    "arcsec": FunctionRule('op("arcsec")', is_unary=True),
    "arcsch": FunctionRule('op("arcsch")', is_unary=True),
    "arcsin": FunctionRule("arcsin", is_unary=True),
    "arctan": FunctionRule("arctan", is_unary=True),
    "arsech": FunctionRule('op("arsech")', is_unary=True),
    "arsinh": FunctionRule('op("arsinh")', is_unary=True),
    "artanh": FunctionRule('op("artanh")', is_unary=True),
    "asin": FunctionRule("arcsin", is_unary=True),
    "asinh": FunctionRule('op("arsinh")', is_unary=True),
    "atan": FunctionRule("arctan", is_unary=True),
    "atanh": FunctionRule('op("artanh")', is_unary=True),
    "ceil": FunctionRule("ceil(", ")", is_wrapped=True),
    "cos": FunctionRule("cos", is_unary=True),
    "cosh": FunctionRule("cosh", is_unary=True),
    "cot": FunctionRule("cot", is_unary=True),
    "coth": FunctionRule("coth", is_unary=True),
    "csc": FunctionRule("csc", is_unary=True),
    "csch": FunctionRule("csch", is_unary=True),
    "exp": FunctionRule("exp", is_unary=True),
    "fabs": FunctionRule("abs(", ")", is_wrapped=True),
    "factorial": FunctionRule("", "!", is_unary=True),
    "floor": FunctionRule("floor(", ")", is_wrapped=True),
    "fsum": FunctionRule("sum", is_unary=True),
    "gamma": FunctionRule("Gamma"),
    "log": FunctionRule("log", is_unary=True),
    "log10": FunctionRule("log_{10}", is_unary=True),
    "log2": FunctionRule("log_2", is_unary=True),
    "prod": FunctionRule("product", is_unary=True),
    "sec": FunctionRule("sec", is_unary=True),
    "sech": FunctionRule("sech", is_unary=True),
    "sin": FunctionRule("sin", is_unary=True),
    "sinh": FunctionRule("sinh", is_unary=True),
    "sqrt": FunctionRule("sqrt(", ")", is_wrapped=True),
    "sum": FunctionRule("sum", is_unary=True),
    "tan": FunctionRule("tan", is_unary=True),
    "tanh": FunctionRule("tanh", is_unary=True),
}

MATH_SYMBOLS = {
    "aleph",
    "alpha",
    "beta",
    "beth",
    "chi",
    "daleth",
    "delta",
    "digamma",
    "epsilon",
    "eta",
    "gamma",
    "gimel",
    "hbar",
    "infty",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nabla",
    "nu",
    "omega",
    "phi",
    "pi",
    "psi",
    "rho",
    "sigma",
    "tau",
    "theta",
    "upsilon",
    "varepsilon",
    "varkappa",
    "varphi",
    "varpi",
    "varrho",
    "varsigma",
    "vartheta",
    "xi",
    "zeta",
    "Delta",
    "Gamma",
    "Lambda",
    "Omega",
    "Phi",
    "Pi",
    "Psi",
    "Sigma",
    "Theta",
    "Upsilon",
    "Xi",
}
