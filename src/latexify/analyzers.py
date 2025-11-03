"""Analyzer functions for specific subtrees."""

from __future__ import annotations

import ast
import copy
import dataclasses
import sys

from latexify import ast_utils, exceptions


@dataclasses.dataclass(frozen=True, eq=False)
class RangeInfo:
    """Information of the range function."""

    # Argument subtrees. These arguments could be shallow copies of the original
    # subtree.
    start: ast.expr
    stop: ast.expr
    step: ast.expr

    # Integer representation of each argument, when it is possible.
    start_int: int | None
    stop_int: int | None
    step_int: int | None


def analyze_range(node: ast.Call) -> RangeInfo:
    """Obtains RangeInfo from a Call subtree.

    Args:
        node: Subtree to be analyzed.

    Returns:
        RangeInfo extracted from `node`.

    Raises:
        LatexifySyntaxError: Analysis failed.
    """
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "range"
        and 1 <= len(node.args) <= 3
    ):
        raise exceptions.LatexifySyntaxError("Unsupported AST for analyze_range.")

    num_args = len(node.args)

    if num_args == 1:
        start = ast_utils.make_constant(0)
        stop = node.args[0]
        step = ast_utils.make_constant(1)
    else:
        start = node.args[0]
        stop = node.args[1]
        step = node.args[2] if num_args == 3 else ast_utils.make_constant(1)

    return RangeInfo(
        start=start,
        stop=stop,
        step=step,
        start_int=ast_utils.extract_int_or_none(start),
        stop_int=ast_utils.extract_int_or_none(stop),
        step_int=ast_utils.extract_int_or_none(step),
    )


class ConstantFolder(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp | ast.Constant:
        match node:
            case ast.BinOp(_, ast.Sub(), ast.UnaryOp(ast.USub())):
                node.op = ast.Add()
                node.right = node.right.operand
                return node
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            match node.op:
                case ast.Add():
                    return ast.Constant(left.value + right.value)
                case ast.Sub():
                    return ast.Constant(left.value - right.value)
                case ast.Mult():
                    return ast.Constant(left.value * right.value)
                case ast.Div():
                    return ast.Constant(left.value / right.value)
                case ast.FloorDiv():
                    return ast.Constant(left.value // right.value)
                case ast.Mod():
                    return ast.Constant(left.value % right.value)
                case ast.LShift():
                    return ast.Constant(left.value << right.value)
                case ast.RShift():
                    return ast.Constant(left.value >> right.value)
        node.left = left
        node.right = right
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.UnaryOp | ast.Constant:
        operand = self.visit(node.operand)
        if isinstance(operand, ast.Constant):
            match node.op:
                case ast.USub():
                    operand.value = -operand.value
                    return operand
        node.operand = operand
        return node


def reduce_stop_parameter(node: ast.expr) -> ast.expr:
    """Adjusts the stop expression of the range.

    This function tries to convert the syntax as follows:
        * n + 1 --> n
        * n + 2 --> n + 1
        * n - 1 --> n - 2

    Args:
        node: The target expression.

    Returns:
        Converted expression.
    """
    node = ConstantFolder().visit(copy.deepcopy(node))
    if isinstance(node, ast.Constant):
        return ast_utils.make_constant(node.value - 1)
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))):
        return ast.BinOp(left=node, op=ast.Sub(), right=ast_utils.make_constant(1))

    # Treatment for Python 3.7.
    rhs = (
        ast.Constant(value=node.right.n)
        if sys.version_info.minor < 8 and isinstance(node.right, ast.Num)
        else node.right
    )

    if not isinstance(rhs, ast.Constant):
        return ast.BinOp(left=node, op=ast.Sub(), right=ast_utils.make_constant(1))

    shift = 1 if isinstance(node.op, ast.Add) else -1

    return (
        node.left
        if rhs.value == shift
        else ast.BinOp(
            left=node.left,
            op=node.op,
            right=ast_utils.make_constant(value=rhs.value - shift),
        )
    )
