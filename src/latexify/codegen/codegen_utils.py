from typing import Any
import re

from latexify import exceptions


def format_float(value: float | complex, sig_figs: int) -> str:
    formatted = "{{:.{rounding}g}}".format(rounding=sig_figs).format(value)
    formatted = re.sub(r"e([+\-0-9]+)", "\\\\mathrm{{e}}{{\\1}}", formatted)
    return formatted


def convert_constant(value: Any, sig_figs: int | None = None) -> str:
    """Helper to convert constant values to LaTeX.

    Args:
        value: A constant value.

    Returns:
        The LaTeX representation of `value`.
    """
    if value is None or isinstance(value, bool):
        return r"\mathrm{" + str(value) + "}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (float, complex)):
        # TODO(odashi): Support other symbols for the imaginary unit than j.
        if sig_figs is not None:
            return format_float(value, sig_figs)
        return str(value)
    if isinstance(value, str):
        return r'\textrm{"' + value + '"}'
    if isinstance(value, bytes):
        return r"\textrm{" + str(value) + "}"
    if value is ...:
        return r"\cdots"
    raise exceptions.LatexifyNotSupportedError(
        f"Unrecognized constant: {type(value).__name__}"
    )
