# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :


"""
Formatting utilities
====================

This file provides classes (`User` class) and terminal
log formatting (`ClickColoredFormatter` class) for the uranus framework.
"""

import click, logging
import utils.shared as shr

# ===========================
# CONSOLE OUTPUT STYLE FORMAT
# ===========================


class User:
    """User context managing output formatting and color preferences.

    Tip: This class is automatically initialized in the module/core via the CLI function,
    and both `colored` and `verbose` are passed to the CLI context.
    """

    COLORED: bool = False
    VERBOSE: bool = False

    def __init__(
        self, colored: bool | None = None, verbose: bool | None = None
    ) -> None:
        self.colored = self.COLORED if colored is None else colored
        self.verbose = False if verbose is None else verbose

    def print_error(self, string: str) -> None:
        """Print error messages."""
        if self.colored:
            click.echo(
                click.style(
                    shr.ERROR_PREFIX,
                    fg=shr.ERROR_OUTPUT_COLOR,
                    bold=shr.ERROR_OUTPUT_BOLD,
                ),
                nl=shr.ERROR_ENABLE_NL,
            )
            click.echo(
                click.style(
                    string,
                    fg=shr.ERROR_OUTPUT_COLOR,
                    bold=shr.ERROR_OUTPUT_BOLD,
                )
            )
        else:
            click.echo(shr.ERROR_PREFIX, nl=False)
            click.echo(string)
        click.get_text_stream("stderr").flush()

    def print_info(self, string: str) -> None:
        """Print informational messages."""
        if self.verbose:
            return
        if self.colored:
            click.echo(
                shr.INFO_PREFIX,
                nl=shr.INFO_ENABLE_NL,
            )
            click.echo(
                click.style(
                    string,
                    fg=shr.INFO_OUTPUT_COLOR,
                    bold=shr.INFO_OUTPUT_BOLD,
                )
            )
        else:
            click.echo(shr.INFO_PREFIX, nl=False)
            click.echo(string)

    def format(self, string: str, **styles) -> str:
        """Return formatted string with given styles if colored is enabled.

        Args:
            string (str): The text to format.
            **styles: Click style keyword arguments (fg, bg, bold, etc.).
        """
        if self.colored:
            return click.style(string, **styles)
        return string


# ====================
# LOGGING OUTPUT STYLE
# ====================


class ClickColoredFormatter(logging.Formatter):
    """Format the log record with custom terminal coloring.

    Respects the standard log format (fmt), timestamps, debug metadata,
    and can be dynamically toggled on or off via the `enabled_color` attribute.
    """

    LEVEL_STYLES = {
        logging.DEBUG: {"fg": "bright_black", "bold": shr.FORMAT_OUTPUT_BOLD},
        logging.INFO: {"fg": "green", "bold": shr.FORMAT_OUTPUT_BOLD},
        logging.WARNING: {"fg": "yellow", "bold": shr.FORMAT_OUTPUT_BOLD},
        logging.ERROR: {"fg": "red", "bold": shr.FORMAT_OUTPUT_BOLD},
        logging.CRITICAL: {"fg": "red", "bold": shr.FORMAT_OUTPUT_BOLD},
    }

    def format(self, record: logging.LogRecord) -> str:
        colored = getattr(self, "enabled_color", True)

        padded_level = f"{record.levelname:<5s}"
        if colored:
            style_args = self.LEVEL_STYLES.get(record.levelno, {})
            colored_level = (
                click.style(padded_level, **style_args)
                if style_args
                else padded_level
            )
        else:
            colored_level = padded_level

        parts = [f"[ {colored_level} ]"]

        if self.usesTime():
            asctime = self.formatTime(record, self.datefmt)
            time_str = f"[ {asctime} ]"
            parts.append(
                click.style(time_str, fg="green") if colored else time_str
            )

        if hasattr(record, "lineno") and record.name:
            meta_str = f"[ {record.name}:{record.lineno} ]"
            parts.append(
                click.style(meta_str, fg="green") if colored else meta_str
            )

        parts.append(record.getMessage())

        return " ".join(parts)
