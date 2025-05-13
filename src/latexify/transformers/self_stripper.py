"""Transformer to strip `self` from function calls and attribute expressions"""

from __future__ import annotations

import ast


class SelfStripper(ast.NodeTransformer):
    """NodeTransformer to remove `self` from function definitions and function calls.

    Example:
        def func(self, x, y, z):
            return self.some_method(x, y, z) + self.some_property

        SelfStripper() will modify the AST to be equivalent to:

        def func(x, y, z):
            return some_method(x, y, z) + some_property
    """

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Visit an Attribute node, transforming `self.x()` to `x()`"""
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            return ast.Name(node.attr, node.ctx)
        else:
            return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Visit an FunctionDef node, transforming `def x(self, y)` to `def x(y)`"""
        if len(node.args.args) > 0 and node.args.args[0].arg == "self":
            node.args.args = node.args.args[1:]
        return self.generic_visit(node)
