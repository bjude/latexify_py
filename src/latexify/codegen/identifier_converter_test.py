"""Tests for latexify.codegen.identifier_converter."""

from __future__ import annotations

import pytest

from latexify.codegen import identifier_converter


@pytest.mark.parametrize(
    "name,use_math_symbols,use_mathrm,escape_underscores,expected",
    [
        ("a", False, True, True, ("a", True)),
        ("_", False, True, True, ('"_"', False)),
        ("aa", False, True, True, ('"aa"', False)),
        ("a1", False, True, True, ('"a1"', False)),
        ("a_", False, True, True, ('"a_"', False)),
        ("_a", False, True, True, ('"_a"', False)),
        ("_1", False, True, True, ('"_1"', False)),
        ("__", False, True, True, ('"__"', False)),
        ("a_a", False, True, True, ('"a_a"', False)),
        ("a__", False, True, True, ('"a__"', False)),
        ("a_1", False, True, True, ('"a_1"', False)),
        ("alpha", False, True, True, ('"alpha"', False)),
        ("alpha", True, True, True, ("alpha", True)),
        ("alphabet", True, True, True, ('"alphabet"', False)),
        ("foo", False, True, True, ('"foo"', False)),
        ("foo", True, True, True, ('"foo"', False)),
        ("foo", True, False, True, ("foo", False)),
        ("aa", False, True, False, ('"aa"', False)),
        ("a_a", False, True, False, ('a_(a)', False)),
        ("a_1", False, True, False, ('a_(1)', False)),
        ("alpha", True, False, False, ("alpha", True)),
        ("alpha_1", True, False, False, ("alpha_(1)", False)),
        ("x_alpha", True, False, False, ("x_(alpha)", False)),
        ("x_alpha_beta", True, False, False, ("x_(alpha_(beta))", False)),
        ("alpha_beta", True, False, False, ("alpha_(beta)", False)),
    ],
)
def test_identifier_converter(
    name: str,
    use_math_symbols: bool,
    use_mathrm: bool,
    escape_underscores: bool,
    expected: tuple[str, bool],
) -> None:
    assert (
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols,
            use_mathrm=use_mathrm,
            escape_underscores=escape_underscores,
        ).convert(name)
        == expected
    )


@pytest.mark.parametrize(
    "name,use_math_symbols,use_mathrm,escape_underscores",
    [
        ("_", False, True, False),
        ("a_", False, True, False),
        ("_a", False, True, False),
        ("_1", False, True, False),
        ("__", False, True, False),
        ("a__", False, True, False),
        ("alpha_", True, False, False),
        ("_alpha", True, False, False),
        ("x__alpha", True, False, False),
    ],
)
def test_identifier_converter_failure(
    name: str,
    use_math_symbols: bool,
    use_mathrm: bool,
    escape_underscores: bool,
) -> None:
    with pytest.raises(ValueError):
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols,
            use_mathrm=use_mathrm,
            escape_underscores=escape_underscores,
        ).convert(name)
