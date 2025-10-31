"""Tests for latexify.codegen.expression_codegen."""

from __future__ import annotations

import ast

import pytest

from latexify import ast_utils, exceptions
from latexify.codegen import expression_codegen


def test_generic_visit() -> None:
    class UnknownNode(ast.AST):
        pass

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Unsupported AST: UnknownNode$",
    ):
        expression_codegen.ExpressionCodegen().visit(UnknownNode())


@pytest.mark.parametrize(
    "code,latex",
    [
        ("()", "(  )"),
        ("(x,)", "( x )"),
        ("(x, y)", "( x, y )"),
        ("(x, y, z)", "( x, y, z )"),
    ],
)
def test_visit_tuple(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Tuple)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("[]", "[  ]"),
        ("[x]", "[ x ]"),
        ("[x, y]", "[ x, y ]"),
        ("[x, y, z]", "[ x, y, z ]"),
    ],
)
def test_visit_list(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.List)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # TODO(odashi): Support set().
        # ("set()", r"\mathopen{}\left\{  \mathclose{}\right\}"),
        ("{x}", "{ x }"),
        ("{x, y}", "{ x, y }"),
        ("{x, y, z}", "{ x, y, z }"),
    ],
)
def test_visit_set(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Set)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("[i for i in n]", "[ i mid(|) i in n ]"),
        ("[i for i in n if i > 0]", "[ i mid(|) ( i in n ) and ( i > 0 ) ]"),
        (
            "[i for i in n if i > 0 if f(i)]",
            "[ i mid(|) ( i in n ) and ( i > 0 ) and ( f ( i ) ) ]",
        ),
        ("[i for k in n for i in k]", "[ i mid(|) k in n, i in k ]"),
        (
            "[i for k in n for i in k if i > 0]",
            "[ i mid(|) k in n, ( i in k ) and ( i > 0 ) ]",
        ),
        (
            "[i for k in n if f(k) for i in k if i > 0]",
            "[ i mid(|) ( k in n ) and ( f ( k ) ), ( i in k ) and ( i > 0 ) ]",
        ),
    ],
)
def test_visit_listcomp(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.ListComp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("{i for i in n}", "{ i mid(|) i in n }"),
        ("{i for i in n if i > 0}", "{ i mid(|) (i in n) and (i > 0) }"),
        ("{i for i in n if i > 0 if f(i)}", "{ i mid(|) (i in n) and ( f(i) ) }"),
        ("{i for k in n for i in k}", "{ i mid(|) k in n, i in k }"),
        (
            "{i for k in n for i in k if i > 0}",
            "{ i mid(|) k in n, ( i in k ) and ( i > 0 ) }",
        ),
        (
            "{i for k in n if f(k) for i in k if i > 0}",
            "{ i mid(|) ( k in n ) and ( f ( k ) ), ( i in k ) and ( i > 0 ) }",
        ),
    ],
)
def test_visit_setcomp(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.SetComp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("foo(x)", 'op("foo") ( x )'),
        ("f(x)", "f ( x )"),
        ("f(-x)", "f ( -x )"),
        ("f(x + y)", "f ( x + y )"),
        ("f(f(x))", "f ( f ( x ) )"),
        ("f(sqrt(x))", "f ( sqrt( x ) )"),
        ("f(sin(x))", "f ( sin x )"),
        ("f(factorial(x))", "f ( x ! )"),
        ("f(x, y)", "f ( x, y )"),
        ("sqrt(x)", "sqrt( x )"),
        ("sqrt(-x)", "sqrt( -x )"),
        ("sqrt(x + y)", "sqrt( x + y )"),
        ("sqrt(f(x))", "sqrt( f ( x ) )"),
        ("sqrt(sqrt(x))", "sqrt( sqrt( x ) )"),
        ("sqrt(sin(x))", "sqrt( sin x )"),
        ("sqrt(factorial(x))", "sqrt( x ! )"),
        ("sin(x)", "sin x"),
        ("sin(-x)", "sin ( -x )"),
        ("sin(x + y)", "sin ( x + y )"),
        ("sin(f(x))", "sin f ( x )"),
        ("sin(sqrt(x))", "sin sqrt( x )"),
        ("sin(sin(x))", "sin sin x"),
        ("sin(factorial(x))", "sin ( x ! )"),
        ("factorial(x)", "x !"),
        ("factorial(-x)", "( -x ) !"),
        ("factorial(x + y)", "( x + y ) !"),
        ("factorial(f(x))", "( f ( x ) ) !"),
        ("factorial(sqrt(x))", "( sqrt( x ) ) !"),
        ("factorial(sin(x))", "( sin x ) !"),
        ("factorial(factorial(x))", "( x ! ) !"),
    ],
)
def test_visit_call(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("log(x)**2", "( log x )^(2)"),
        ("log(x**2)", "log ( x^(2) )"),
        ("log(x**2)**3", "( log ( x^(2) ) )^(3)"),
    ],
)
def test_visit_call_with_pow(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, (ast.Call, ast.BinOp))
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        # No arguments
        ("()", " ( )"),
        # No comprehension
        ("(x)", " x"),
        ("([1, 2])", " [ 1, 2 ]"),
        ("({1, 2})", " { 1, 2 }"),
        ("(f(x))", " f ( x )"),
        # Single comprehension
        ("(i for i in x)", "_(i in x)^() (i)"),
        ("(i for i in [1, 2])", "_(i in [ 1, 2 ])^() (i)"),
        ("(i for i in {1, 2})", "_(i in { 1, 2 })^() (i)"),
        ("(i for i in f(x))", "_(i in f ( x ))^() (i)"),
        ("(i for i in range(n))", "_(i = 0)^(n - 1) (i)"),
        ("(i for i in range(n + 1))", "_(i = 0)^(n) (i)"),
        ("(i for i in range(n + 2))", "_(i = 0)^(n + 1) (i)"),
        ("(i for i in range(n - -1))", "_(i = 0)^(n) (i)"),
        ("(i for i in range(n - 1))", "_(i = 0)^(n - 2) (i)"),
        ("(i for i in range(n + m))", "_(i = 0)^(n + m - 1) (i)"),
        ("(i for i in range(n - m))", "_(i = 0)^(n - m - 1) (i)"),
        ("(i for i in range(3))", "_(i = 0)^(2) (i)"),
        ("(i for i in range(3 + 1))", "_(i = 0)^(3) (i)"),
        ("(i for i in range(3 + 2))", "_(i = 0)^(4) (i)"),
        ("(i for i in range(3 - 1))", "_(i = 0)^(1) (i)"),
        ("(i for i in range(3 - -1))", "_(i = 0)^(3) (i)"),
        ("(i for i in range(3 + m))", "_(i = 0)^(3 + m - 1) (i)"),
        ("(i for i in range(3 - m))", "_(i = 0)^(3 - m - 1) (i)"),
        ("(i for i in range(n, m))", "_(i = n)^(m - 1) (i)"),
        ("(i for i in range(1, m))", "_(i = 1)^(m - 1) (i)"),
        ("(i for i in range(n, 3))", "_(i = n)^(2) (i)"),
        # FIXME(BJ): This could be done differently by specifying modulo = 0
        ("(i for i in range(n, m, k))", '_(i in op("range") ( n, m, k ) )^() (i)'),
    ],
)
def test_visit_call_sum_prod(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("fsum", "sum"), ("sum", "sum"), ("prod", "product")]:
        node = ast_utils.parse_expr(src_fn + src_suffix)
        assert isinstance(node, ast.Call)
        assert (
            expression_codegen.ExpressionCodegen().visit(node) == dest_fn + dest_suffix
        )


@pytest.mark.parametrize(
    "code,latex",
    [
        # 2 clauses
        ("sum(i for y in x for i in y)", "sum_(y in x)^() sum_(i in y)^() (i)"),
        # 3 clauses
        (
            "sum(i for y in x for z in y for i in z)",
            "sum_(y in x)^() sum_(z in y)^() sum_(i in z)^() (i)",
        ),
        # 2 clauses
        (
            "prod(i for y in x for i in y)",
            "product_(y in x)^() product_(i in y)^() (i)",
        ),
        # 3 clauses
        (
            "prod(i for y in x for z in y for i in z)",
            "product_(y in x)^() product_(z in y)^() product_(i in z)^() (i)",
        ),
        # reduce stop parameter
        ("sum(i for i in range(n+1))", "sum_(i = 0)^(n) (i)"),
        ("sum(i for i in range(n-1))", "sum_(i = 0)^(n - 2) (i)"),
        # reduce stop parameter
        ("prod(i for i in range(n+1))", "product_(i = 0)^(n) (i)"),
        ("prod(i for i in range(n-1))", "product_(i = 0)^(n - 2) (i)"),
    ],
)
def test_visit_call_sum_prod_multiple_comprehension(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        ("(i for i in x if i < y)", "_(( i in x ) and ( i < y))^() (i)"),
        (
            "(i for i in x if i < y if f(i))",
            "_(( i in x ) and ( i < y ) and ( f ( i ) ))^() (i)",
        ),
    ],
)
def test_visit_call_sum_prod_with_if(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("sum", "sum"), ("prod", "product")]:
        node = ast_utils.parse_expr(src_fn + src_suffix)
        assert isinstance(node, ast.Call)
        assert (
            expression_codegen.ExpressionCodegen().visit(node) == dest_fn + dest_suffix
        )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x if x < y else y", 'cases( x ","& "if" x < y, y ","& "otherwise")'),
        (
            "x if x < y else (y if y < z else z)",
            'cases( x ","& "if" x < y, y ","& "if" y < z, z ","& "otherwise")',
        ),
        (
            "x if x < y else (y if y < z else (z if z < w else w))",
            'cases( x ","& "if" x < y, y ","& "if" y < z, z ","& "if" z < w, w ","& "otherwise")',
        ),
    ],
)
def test_if_then_else(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.IfExp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # x op y
        ("x**y", "x^(y)"),
        ("x * y", "x y"),
        ("x @ y", "x y"),
        ("x / y", "frac(x, y)"),
        ("x // y", "floor(frac(x, y))"),
        ("x % y", "x op(%) y"),
        ("x + y", "x + y"),
        ("x - y", "x - y"),
        ("x << y", "x << y"),
        ("x >> y", "x >> y"),
        ("x & y", "x op(&) y"),
        ("x ^ y", "x plus.o y"),
        ("x | y", "x op(|) y"),
        # (x op y) op z
        ("(x**y)**z", "( x^(y) )^(z)"),
        ("(x * y) * z", "x y z"),
        ("(x @ y) @ z", "x y z"),
        ("(x / y) / z", "frac(frac(x, y), z)"),
        ("(x // y) // z", "floor(frac(floor(frac(x, y)), z))"),
        ("(x % y) % z", "x op(%) y op(%) z"),
        ("(x + y) + z", "x + y + z"),
        ("(x - y) - z", "x - y - z"),
        ("(x << y) << z", "x << y << z"),
        ("(x >> y) >> z", "x >> y >> z"),
        ("(x & y) & z", "x op(&) y op(&) z"),
        ("(x ^ y) ^ z", "x plus.o y plus.o z"),
        ("(x | y) | z", "x op(|) y (|) z"),
        # x op (y op z)
        ("x**(y**z)", "x^(y^(z))"),
        ("x * (y * z)", "x y z"),
        ("x @ (y @ z)", "x y z"),
        ("x / (y / z)", "frac(x, frac(y, z))"),
        ("x // (y // z)", "floor(frac(x, floor(frac(y, z))))"),
        ("x % (y % z)", "x op(%) ( y op(%) z )"),
        ("x + (y + z)", "x + y + z"),
        ("x - (y - z)", "x - ( y - z )"),
        ("x << (y << z)", "x << ( y << z )"),
        ("x >> (y >> z)", "x >> ( y >> z )"),
        ("x & (y & z)", "x op(&) y op(&) z"),
        ("x ^ (y ^ z)", "x plus.o y plus.o z"),
        ("x | (y | z)", "x op(|) y op(|) z"),
        # x OP y op z
        ("x**y * z", "x^(y) z"),
        ("x * y + z", "x y + z"),
        ("x @ y + z", "x y + z"),
        ("x / y + z", "frac(x, y) + z"),
        ("x // y + z", "floor(frac(x, y)) + z"),
        ("x % y + z", "x op(%) y + z"),
        ("x + y << z", "x + y << z"),
        ("x - y << z", "x - y << z"),
        ("x << y & z", "x << y op(&) z"),
        ("x >> y & z", "x >> y op(&) z"),
        ("x & y ^ z", "x op(&) y plus.o z"),
        ("x ^ y | z", "x plus.o y op(|) z"),
        # x OP (y op z)
        ("x**(y * z)", "x^(y z)"),
        ("x * (y + z)", "x dot ( y + z )"),
        ("x @ (y + z)", "x dot ( y + z )"),
        ("x / (y + z)", "frac(x, y + z)"),
        ("x // (y + z)", "floor(frac(x, y + z))"),
        ("x % (y + z)", "x op(%) ( y + z )"),
        ("x + (y << z)", "x + ( y << z )"),
        ("x - (y << z)", "x - ( y << z )"),
        ("x << (y & z)", "x << ( y op(&) z )"),
        ("x >> (y & z)", "x >> ( y op(&) z )"),
        ("x & (y ^ z)", "x op(&) ( y plus.o z )"),
        ("x ^ (y | z)", "x plus.o ( y op(|) z )"),
        # x op y OP z
        ("x * y**z", "x y^(z)"),
        ("x + y * z", "x + y z"),
        ("x + y @ z", "x + y z"),
        ("x + y / z", "x + frac(y, z)"),
        ("x + y // z", "x + floor(frac(y, z))"),
        ("x + y % z", "x + y op(%) z"),
        ("x << y + z", "x << y + z"),
        ("x << y - z", "x << y - z"),
        ("x & y << z", "x op(&) y << z"),
        ("x & y >> z", "x op(&) y >> z"),
        ("x ^ y & z", "x plus.o y op(&) z"),
        ("x | y ^ z", "x op(|) y plus.o z"),
        # (x op y) OP z
        ("(x * y)**z", "( x y )^(z)"),
        ("(x + y) * z", "( x + y ) z"),
        ("(x + y) @ z", "( x + y ) z"),
        ("(x + y) / z", "frac(x + y, z)"),
        ("(x + y) // z", "floor(frac(x + y, z))"),
        ("(x + y) % z", "( x + y ) op(%) z"),
        ("(x << y) + z", "( x << y ) + z"),
        ("(x << y) - z", "( x << y ) - z"),
        ("(x & y) << z", "( x op(&) y ) << z"),
        ("(x & y) >> z", "( x op(&) y ) >> z"),
        ("(x ^ y) & z", "( x plus.o y ) op(&) z"),
        ("(x | y) ^ z", "( x op(|) y ) plus.o z"),
        # is_wrapped
        ("(x // y)**z", "floor(frac(x, y))^(z)"),
        # With Call
        ("x**f(y)", "x^(f ( y ))"),
        ("f(x)**y", "( f ( x ) )^(y)"),
        ("x * f(y)", "x dot f ( y )"),
        ("f(x) * y", "f ( x ) dot y"),
        ("x / f(y)", "frac(x, f ( y ))"),
        ("f(x) / y", "frac(f ( x ), y)"),
        ("x + f(y)", "x + f ( y )"),
        ("f(x) + y", "f ( x ) + y"),
        # With is_wrapped Call
        ("sqrt(x) ** y", "sqrt( x )^(y)"),
        # With UnaryOp
        ("x**-y", "x^(-y)"),
        ("(-x)**y", "( -x )^(y)"),
        ("x * -y", "x dot -y"),
        ("-x * y", "-x y"),
        ("x / -y", "frac(x, -y)"),
        ("-x / y", "frac(-x, y)"),
        ("x + -y", "x + -y"),
        ("-x + y", "-x + y"),
        # With Compare
        ("x**(y == z)", "x^(y = z)"),
        ("(x == y)**z", "( x = y )^(z)"),
        ("x * (y == z)", "x dot ( y = z )"),
        ("(x == y) * z", "( x = y ) z"),
        ("x / (y == z)", "frac(x, y = z)"),
        ("(x == y) / z", "frac(x = y, z)"),
        ("x + (y == z)", "x + ( y = z )"),
        ("(x == y) + z", "( x = y ) + z"),
        # With BoolOp
        ("x**(y and z)", "x^(y and z)"),
        ("(x and y)**z", "( x and y )^(z)"),
        ("x * (y and z)", "x dot ( y and z )"),
        ("(x and y) * z", "( x and y ) z"),
        ("x / (y and z)", "frac(x, y and z)"),
        ("(x and y) / z", "frac(x and y, z)"),
        ("x + (y and z)", "x + ( y and z )"),
        ("(x and y) + z", "( x and y ) + z"),
    ],
)
def test_visit_binop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BinOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("+x", "+x"),
        ("-x", "-x"),
        ("~x", "~x"),
        ("not x", "not x"),
        # With Call
        ("+f(x)", "+f ( x )"),
        ("-f(x)", "-f ( x )"),
        ("~f(x)", "~f ( x )"),
        ("not f(x)", "not f ( x )"),
        # With BinOp
        ("+(x + y)", "+( x + y )"),
        ("-(x + y)", "-( x + y )"),
        ("~(x + y)", "~( x + y )"),
        ("not x + y", "not ( x + y )"),
        # With Compare
        ("+(x == y)", "+( x = y )"),
        ("-(x == y)", "-( x = y )"),
        ("~(x == y)", "~  x = y )"),
        ("not x == y", "not ( x = y )"),
        # With BoolOp
        ("+(x and y)", "+( x and y )"),
        ("-(x and y)", "-( x and y )"),
        ("~(x and y)", "~(x and y)"),
        ("not (x and y)", "not ( x and y )"),
    ],
)
def test_visit_unaryop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.UnaryOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # 1 comparator
        ("a == b", "a = b"),
        ("a > b", "a > b"),
        ("a >= b", "a >= b"),
        ("a in b", "a in b"),
        ("a is b", "a equiv b"),
        ("a is not b", "a not equiv b"),
        ("a < b", "a < b"),
        ("a <= b", "a <= b"),
        ("a != b", "a eq.not b"),
        ("a not in b", "a in.not b"),
        # 2 comparators
        ("a == b == c", "a = b = c"),
        ("a == b > c", "a = b > c"),
        ("a == b >= c", "a = b >= c"),
        ("a == b < c", "a = b < c"),
        ("a == b <= c", "a = b <= c"),
        ("a > b == c", "a > b = c"),
        ("a > b > c", "a > b > c"),
        ("a > b >= c", "a > b >= c"),
        ("a >= b == c", "a >= b = c"),
        ("a >= b > c", "a >= b > c"),
        ("a >= b >= c", "a >= b >= c"),
        ("a < b == c", "a < b = c"),
        ("a < b < c", "a < b < c"),
        ("a < b <= c", "a < b <= c"),
        ("a <= b == c", "a <= b = c"),
        ("a <= b < c", "a <= b < c"),
        ("a <= b <= c", "a <= b <= c"),
        # With Call
        ("a == f(b)", "a = f ( b )"),
        ("f(a) == b", "f ( a ) = b"),
        # With BinOp
        ("a == b + c", "a = b + c"),
        ("a + b == c", "a + b = c"),
        # With UnaryOp
        ("a == -b", "a = -b"),
        ("-a == b", "-a = b"),
        ("a == (not b)", "a = not b"),
        ("(not a) == b", "not a = b"),
        # With BoolOp
        ("a == (b and c)", "a = ( b and c )"),
        ("(a and b) == c", "( a and b ) = c"),
    ],
)
def test_visit_compare(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Compare)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("a and b", "a and b"),
        ("a and b and c", "a and b and c"),
        ("a or b", "a or b"),
        ("a or b or c", "a or b or c"),
        ("a or b and c", "a or b and c"),
        ("(a or b) and c", "( a or b ) and c"),
        ("a and b or c", "a and b or c"),
        ("a and (b or c)", "a and ( b or c )"),
        # With Call
        ("a and f(b)", "a and f ( b )"),
        ("f(a) and b", "f ( a ) and b"),
        ("a or f(b)", "a or f ( b )"),
        ("f(a) or b", "f ( a ) or b"),
        # With BinOp
        ("a and b + c", "a and b + c"),
        ("a + b and c", "a + b and c"),
        ("a or b + c", "a or b + c"),
        ("a + b or c", "a + b or c"),
        # With UnaryOp
        ("a and not b", "a and not b"),
        ("not a and b", "not a and b"),
        ("a or not b", "a or not b"),
        ("not a or b", "not a or b"),
        # With Compare
        ("a and b == c", "a and b = c"),
        ("a == b and c", "a = b and c"),
        ("a or b == c", "a or b = c"),
        ("a == b or c", "a = b or c"),
    ],
)
def test_visit_boolop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BoolOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    {
        ("0", "0"),
        ("1", "1"),
        ("0.0", "0.0"),
        ("1.5", "1.5"),
        ("0.0j", "0j"),
        ("1.0j", "1j"),
        ("1.5j", "1.5j"),
        ('"abc"', "quote[abc]"),
        ('b"abc"', "b#quote[abc]"),
        ("None", '"None"'),
        ("False", '"False"'),
        ("True", '"True"'),
        ("...", "dots.c"),
    },
)
def test_visit_constant(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Constant)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x[0]", "x_(0)"),
        ("x[0][1]", "x_(0, 1)"),
        ("x[0][1][2]", "x_(0, 1, 2)"),
        ("x[foo]", 'x_("foo")'),
        ("x[floor(x)]", "x_(floor( x ))"),
    ],
)
def test_visit_subscript(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Subscript)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a - b", "a without b"),
        ("a & b", "a cap b"),
        ("a ^ b", "a triangle b"),
        ("a | b", "a union b"),
    ],
)
def test_visit_binop_use_set_symbols(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BinOp)
    assert (
        expression_codegen.ExpressionCodegen(use_set_symbols=True).visit(tree) == latex
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a < b", "a subset b"),
        ("a <= b", "a subset.eq b"),
        ("a > b", "a supset b"),
        ("a >= b", "a supset.eq b"),
    ],
)
def test_visit_compare_use_set_symbols(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Compare)
    assert (
        expression_codegen.ExpressionCodegen(use_set_symbols=True).visit(tree) == latex
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("array(1)", 'op("array") ( 1 )'),
        ("array([])", 'op("array")([])'),
        ("array([1])", 'mat(delim:"[", 1 )'),
        ("array([1, 2, 3])", 'mat(delim:"[", 1, 2, 3 )'),
        ("array([[]])", 'op("array")([[]])'),
        ("array([[1]])", 'mat(delim:"[", 1 )'),
        ("array([[1], [2], [3]])", 'mat(delim:"[", 1; 2; 3 )'),
        ("array([[1], [2], [3, 4]])", 'op("array")([[ 1 ], [ 2 ], [ 3, 4 ]])'),
        ("array([[1, 2], [3, 4], [5, 6]])", 'mat(delim:"[", 1, 2; 3, 4; 5, 6 )'),
        # Only checks two cases for ndarray.
        ("ndarray(1)", 'op("ndarray") ( 1 )'),
        ("ndarray([1])", 'mat(delim:"[", 1 )'),
    ],
)
def test_numpy_array(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("zeros(0)", "bold(0)^(1 times 0)"),
        ("zeros(1)", "bold(0)^(1 times 1)"),
        ("zeros(2)", "bold(0)^(1 times 2)"),
        ("zeros(())", "0"),
        ("zeros((0,))", "bold(0)^(1 times 0)"),
        ("zeros((1,))", "bold(0)^(1 times 1)"),
        ("zeros((2,))", "bold(0)^(1 times 2)"),
        ("zeros((0, 0))", "bold(0)^(0 times 0)"),
        ("zeros((1, 1))", "bold(0)^(1 times 1)"),
        ("zeros((2, 3))", "bold(0)^(2 times 3)"),
        ("zeros((0, 0, 0))", "bold(0)^(0 times 0 times 0)"),
        ("zeros((1, 1, 1))", "bold(0)^(1 times 1 times 1)"),
        ("zeros((2, 3, 5))", "bold(0)^(2 times 3 times 5)"),
        # Unsupported
        ("zeros()", 'op("zeros") ( )'),
        ("zeros(x)", 'op("zeros") ( x )'),
        ("zeros(0, x)", 'op("zeros") ( 0, x )'),
        ("zeros((x,))", 'op("zeros") ( ( x ) )'),
    ],
)
def test_zeros(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("identity(0)", "bold(I)_(0)"),
        ("identity(1)", "bold(I)_(1)"),
        ("identity(2)", "bold(I)_(2)"),
        # Unsupported
        ("identity()", 'op("identity") ( )'),
        ("identity(x)", 'op("identity") ( x )'),
        ("identity(0, x)", 'op("identity") ( 0, x )'),
    ],
)
def test_identity(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("transpose(A)", "bold(A)^(T)"),
        ("transpose(b)", "bold(b)^(T)"),
        # Unsupported
        ("transpose()", 'op("transpose") ( )'),
        ("transpose(2)", 'op("transpose") ( 2 )'),
        ("transpose(a, (1, 0))", 'op("transpose") ( a, ( 1, 0 ) )'),
    ],
)
def test_transpose(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("det(A)", "det ( bold(A) )"),
        ("det(b)", "det ( bold(b) )"),
        ("det([[1, 2], [3, 4]])", 'det ( mat(delim:"[" 1, 2; 3, 4 ) )'),
        (
            "det([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            'det ( mat(delim:"[" 1, 2, 3; 4, 5, 6; 7, 8, 9 ) )',
        ),
        # Unsupported
        ("det()", "det( )"),
        ("det(2)", "det( 2 )"),
        ("det(a, (1, 0))", "det( a, ( 1, 0 ) )"),
    ],
)
def test_determinant(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("matrix_rank(A)", 'op("rank") ( bold(A) )'),
        ("matrix_rank(b)", 'op("rank") ( bold(b) )'),
        ("matrix_rank([[1, 2], [3, 4]])", 'op("rank") ( mat(delim:"[", 1, 2; 3, 4 ) )'),
        (
            "matrix_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            'op("rank") ( mat(delim:"[", 1, 2, 3; 4, 5, 6; 7, 8, 9 ) )',
        ),
        # Unsupported
        ("matrix_rank()", 'op("matrix_rank") ( )'),
        ("matrix_rank(2)", 'op("matrix_rank") ( 2 )'),
        ("matrix_rank(a, (1, 0))", 'op("matrix_rank") ( a, ( 1, 0 ) )'),
    ],
)
def test_matrix_rank(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("matrix_power(A, 2)", "bold(A)^(2)"),
        ("matrix_power(b, 2)", "bold(b)^(2)"),
        ("matrix_power([[1, 2], [3, 4]], 2)", 'mat(delim:"[", 1, 2; 3, 4 )^(2)'),
        (
            "matrix_power([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 42)",
            'mat(delim:"[", 1, 2, 3; 4, 5, 6; 7, 8, 9 )^(42)',
        ),
        # Unsupported
        ("matrix_power()", 'op("matrix_power") ( )'),
        ("matrix_power(2)", 'op("matrix_power") ( 2 )'),
        ("matrix_power(a, (1, 0))", 'op("matrix_power") ( a, ( 1, 0) )'),
    ],
)
def test_matrix_power(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("inv(A)", "bold(A)^(-1)"),
        ("inv(b)", "bold(b)^(-1)"),
        (
            "inv([[1, 2], [3, 4]])",
            'mat(delim:"[", 1, 2; 3, 4 )^(-1)',
        ),
        (
            "inv([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            'mat(delim:"[", 1, 2, 3; 4, 5, 6; 7, 8, 9 )^(-1)',
        ),
        # Unsupported
        ("inv()", 'op("inv") ( )'),
        ("inv(2)", 'op("inv") ( 2 )'),
        ("inv(a, (1, 0))", 'op("inv") ( a, ( 1, 0) )'),
    ],
)
def test_inv(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("pinv(A)", "bold(A)^(+)"),
        ("pinv(b)", "bold(b)^(+)"),
        ("pinv([[1, 2], [3, 4]])", 'mat(delim:"[", 1, 2; 3, 4 )^(+)'),
        (
            "pinv([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            'mat(delim:"[", 1, 2, 3; 4, 5, 6; 7, 8, 9 )^(+)',
        ),
        # Unsupported
        ("pinv()", 'op("pinv") ( )'),
        ("pinv(2)", 'op("pinv") ( 2 )'),
        ("pinv(a, (1, 0))", 'op("pinv") ( a, ( 1, 0) )'),
    ],
)
def test_pinv(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


# Check list for #89.
# https://github.com/google/latexify_py/issues/89#issuecomment-1344967636
@pytest.mark.parametrize(
    "left,right,latex",
    [
        ("2", "3", "2 dot.op 3"),
        ("2", "y", "2 y"),
        ("2", "beta", "2 beta"),
        ("2", "bar", '2 "bar"'),
        ("2", "g(y)", "2 g ( y )"),
        ("2", "(u + v)", "2 ( u + v )"),
        ("x", "3", "x dot.op 3"),
        ("x", "y", "x y"),
        ("x", "beta", "x beta"),
        ("x", "bar", 'x dot.op "bar"'),
        ("x", "g(y)", "x dot.op g ( y )"),
        ("x", "(u + v)", "x dot.op ( u + v )"),
        ("alpha", "3", "alpha dot.op 3"),
        ("alpha", "y", "alpha y"),
        ("alpha", "beta", "alpha beta"),
        ("alpha", "bar", 'alpha dot.op "bar"'),
        ("alpha", "g(y)", "alpha dot.op g ( y )"),
        ("alpha", "(u + v)", "alpha dot.op ( u + v )"),
        ("foo", "3", '"foo" dot.op 3'),
        ("foo", "y", '"foo" dot.op y'),
        ("foo", "beta", '"foo" dot.op beta'),
        ("foo", "bar", '"foo" dot.op "bar"'),
        ("foo", "g(y)", '"foo" dot.op g ( y )'),
        ("foo", "(u + v)", '"foo" dot.op ( u + v )'),
        ("f(x)", "3", "f ( x ) dot.op 3"),
        ("f(x)", "y", "f ( x ) dot.op y"),
        ("f(x)", "beta", "f ( x ) dot.op beta"),
        ("f(x)", "bar", 'f ( x ) dot.op "bar"'),
        ("f(x)", "g(y)", "f ( x ) dot.op g ( y )"),
        ("f(x)", "(u + v)", "f ( x ) dot.op ( u + v )"),
        ("(s + t)", "3", "( s + t ) dot.op 3"),
        ("(s + t)", "y", "( s + t ) y"),
        ("(s + t)", "beta", "( s + t ) beta"),
        ("(s + t)", "bar", '( s + t ) "bar"'),
        ("(s + t)", "g(y)", "( s + t ) g ( y )"),
        ("(s + t)", "(u + v)", "( s + t ) ( u + v )"),
    ],
)
def test_remove_multiply(left: str, right: str, latex: str) -> None:
    for op in ["*", "@"]:
        tree = ast_utils.parse_expr(f"{left} {op} {right}")
        assert isinstance(tree, ast.BinOp)
        assert (
            expression_codegen.ExpressionCodegen(use_math_symbols=True).visit(tree)
            == latex
        )
