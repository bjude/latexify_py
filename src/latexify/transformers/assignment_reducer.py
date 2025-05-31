"""NodeTransformer to reduce assigned expressions."""

from __future__ import annotations

import ast
from typing import Any

from latexify import ast_utils, exceptions


class AssignmentReducer(ast.NodeTransformer):
    """NodeTransformer to reduce assigned expressions.

    This class replaces a functions with multiple assignments to a function with only
    single return.

    Example:
        def f(x):
            y = 2 + x
            z = 3 * y
            return 4 + z

        AssignmentReducer modifies the function above to below:

        def f(x):
            return 4 + 3 * (2 + x)
    """

    _retained: set[str]
    _assignments: dict[str, ast.expr] | None = None

    def __init__(self, retained: set[str] | None = None):
        self._retained = retained or set()

    # TODO(odashi):
    # Currently, this function does not care much about some expressions, e.g.,
    # comprehensions or lambdas, which introduces inner scopes.
    # It may cause some mistakes in the resulting AST.
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Visit a FunctionDef node."""
        # Push stack
        parent_assignments = self._assignments
        self._assignments = {}

        for child in node.body[:-1]:
            if not isinstance(child, ast.Assign):
                raise exceptions.LatexifyNotSupportedError(
                    "AssignmentReducer supports only Assign nodes, "
                    f"but got: {type(child).__name__}"
                )

            value = self.visit(child.value)

            for target in child.targets:
                if not isinstance(target, ast.Name):
                    raise exceptions.LatexifyNotSupportedError(
                        "AssignmentReducer does not recognize list/tuple "
                        "decomposition."
                    )
                self._assignments[target.id] = value

        return_original = node.body[-1]

        if not isinstance(return_original, (ast.Return, ast.If)):
            raise exceptions.LatexifySyntaxError(
                f"Unsupported last statement: {type(return_original).__name__}"
            )

        return_transformed = self.visit(return_original)
        retained = [
            ast.Assign([ast.Name(name, ctx=ast.Load())], expr)
            for name, expr in (self._assignments or {}).items()
            if name in self._retained
        ]

        # Pop stack
        self._assignments = parent_assignments
        type_params = getattr(node, "type_params", [])
        return ast_utils.create_function_def(
            name=node.name,
            args=node.args,
            body=retained + [return_transformed],
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_params=type_params,
        )

    def visit_Name(self, node: ast.Name) -> Any:
        """Visit a Name node."""
        if self._assignments is not None and node.id not in self._retained:
            return self._assignments.get(node.id, node)

        return node
