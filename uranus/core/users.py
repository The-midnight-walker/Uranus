# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :


"""
Users utilities
====================

This file provides classes (`User` class)
"""

from types import SimpleNamespace, SimpleNamespace as sns

import click


class User:
    """User context managing output formatting and color preferences.

    Tip: This class is automatically initialized in the module/core via the CLI
    function, and both `colored` and `verbose` are passed to the CLI context.
    """

    COLORED: bool = False
    VERBOSE: bool = False

    OUTPUT_FORMATS = sns(
        info=sns(
            color="cyan",
            nl=True,
            bold=False,
            prefix="",
        ),
        success=sns(
            color="green",
            nl=True,
            bold=False,
            prefix="",
        ),
        failure=sns(
            color="red",
            nl=True,
            bold=False,
            prefix="",
        ),
        warning=sns(
            color="bright_red",
            nl=True,
            bold=False,
            prefix="[ WARN  ]",
        ),
        error=sns(
            color="red",
            nl=True,
            bold=False,
            prefix="[ ERROR ]",
        ),
    )

    @classmethod
    def configure(
        cls,
        colored: bool | None = None,
        verbose: bool | None = None,
        output_formats: SimpleNamespace | None = None,
    ) -> None:
        """Configure global output preferences."""

        if colored is not None:
            cls.COLORED = colored

        if verbose is not None:
            cls.VERBOSE = verbose

        if output_formats is not None:
            cls.OUTPUT_FORMATS = output_formats

    @classmethod
    def _emit(
        cls,
        level: str,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Format and emit a message."""

        fmt = getattr(cls.OUTPUT_FORMATS, level)

        prefix = fmt.prefix if prefix is None else prefix
        nl = fmt.nl if nl is None else nl
        bold = fmt.bold if bold is None else bold
        fg = fmt.color if fg is None else fg

        if level == "info" and not cls.VERBOSE:
            return

        if prefix:
            prefix = cls.Formatter.format(
                prefix,
                fg=fg if cls.COLORED else None,
                bold=bold,
            )
            string = f"{prefix} {string}"

        is_error = level in {"error", "warning"}
        stream = click.get_text_stream("stderr" if is_error else "stdout")

        click.echo(string, file=stream, nl=nl)
        stream.flush()

    @classmethod
    def print_err(
        cls,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Print error messages."""

        cls._emit("error", string, prefix, nl, bold, fg)

    @classmethod
    def print_info(
        cls,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Print informational messages."""

        cls._emit("info", string, prefix, nl, bold, fg)

    @classmethod
    def print_success(
        cls,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Print success messages."""

        cls._emit("success", string, prefix, nl, bold, fg)

    @classmethod
    def print_failure(
        cls,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Print failure messages."""

        cls._emit("failure", string, prefix, nl, bold, fg)

    @classmethod
    def print_warn(
        cls,
        string: str,
        prefix: str | None = None,
        nl: bool | None = None,
        bold: bool | None = None,
        fg: str | None = None,
    ) -> None:
        """Print warning messages."""

        cls._emit("warning", string, prefix, nl, bold, fg)

    @staticmethod
    def print(string: str, nl: bool = True) -> None:
        """Print plain text."""

        click.echo(string, nl=nl)

    class Formatter:
        """Formatter supporting optional terminal colors."""

        @classmethod
        def format(cls, string: str, **styles) -> str:
            """Format a string with Click styles"""
            if "fg" in styles and not User.COLORED:
                styles["fg"] = None

            return click.style(string, **styles)
