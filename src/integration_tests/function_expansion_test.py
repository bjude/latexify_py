"""End-to-end test cases of function expansion."""

from __future__ import annotations

import math

from integration_tests import integration_utils


def test_atan2() -> None:
    def solve(x, y):
        return math.atan2(y, x)

    latex = 'op("solve")( x, y ) = arctan ( frac(y, x) )'
    integration_utils.check_function(solve, latex, expand_functions={"atan2"})


def test_atan2_nested() -> None:
    def solve(x, y):
        return math.atan2(math.exp(y), math.exp(x))

    latex = 'op("solve")( x, y ) = arctan ( frac(e^(y), e^(x)) )'
    integration_utils.check_function(solve, latex, expand_functions={"atan2", "exp"})


def test_exp() -> None:
    def solve(x):
        return math.exp(x)

    latex = 'op("solve")( x ) = e^(x)'
    integration_utils.check_function(solve, latex, expand_functions={"exp"})


def test_exp_nested() -> None:
    def solve(x):
        return math.exp(math.exp(x))

    latex = 'op("solve")( x ) = e^(e^(x))'
    integration_utils.check_function(solve, latex, expand_functions={"exp"})


def test_exp2() -> None:
    def solve(x):
        return math.exp2(x)

    latex = 'op("solve")( x ) = 2^(x)'
    integration_utils.check_function(solve, latex, expand_functions={"exp2"})


def test_exp2_nested() -> None:
    def solve(x):
        return math.exp2(math.exp2(x))

    latex = 'op("solve")( x ) = 2^(2^(x))'
    integration_utils.check_function(solve, latex, expand_functions={"exp2"})


def test_expm1() -> None:
    def solve(x):
        return math.expm1(x)

    latex = 'op("solve")( x ) = exp x - 1'
    integration_utils.check_function(solve, latex, expand_functions={"expm1"})


def test_expm1_nested() -> None:
    def solve(x, y, z):
        return math.expm1(math.pow(y, z))

    latex = 'op("solve")( x, y, z ) = e^(y^(z)) - 1'
    integration_utils.check_function(
        solve, latex, expand_functions={"expm1", "exp", "pow"}
    )


def test_hypot_without_attribute() -> None:
    from math import hypot

    def solve(x, y, z):
        return hypot(x, y, z)

    latex = 'op("solve")( x, y, z ) = sqrt( x^(2) + y^(2) + z^(2) )'
    integration_utils.check_function(solve, latex, expand_functions={"hypot"})


def test_hypot() -> None:
    def solve(x, y, z):
        return math.hypot(x, y, z)

    latex = 'op("solve")( x, y, z ) = sqrt( x^(2) + y^(2) + z^(2) )'
    integration_utils.check_function(solve, latex, expand_functions={"hypot"})


def test_hypot_nested() -> None:
    def solve(a, b, x, y):
        return math.hypot(math.hypot(a, b), x, y)

    latex = (
        'op("solve")( a, b, x, y ) = sqrt( sqrt( a^(2) + b^(2) )^(2) + x^(2) + y^(2) )'
    )
    integration_utils.check_function(solve, latex, expand_functions={"hypot"})


def test_log1p() -> None:
    def solve(x):
        return math.log1p(x)

    latex = 'op("solve")( x ) = log ( 1 + x )'
    integration_utils.check_function(solve, latex, expand_functions={"log1p"})


def test_log1p_nested() -> None:
    def solve(x):
        return math.log1p(math.exp(x))

    latex = 'op("solve")( x ) = log ( 1 + e^(x) )'
    integration_utils.check_function(solve, latex, expand_functions={"log1p", "exp"})


def test_pow_nested() -> None:
    def solve(w, x, y, z):
        return math.pow(math.pow(w, x), math.pow(y, z))

    latex = 'op("solve")( w, x, y, z ) = ( w^(x) )^(y^(z))'
    integration_utils.check_function(solve, latex, expand_functions={"pow"})


def test_pow() -> None:
    def solve(x, y):
        return math.pow(x, y)

    latex = 'op("solve")( x, y ) = x^(y)'
    integration_utils.check_function(solve, latex, expand_functions={"pow"})
