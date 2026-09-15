# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :


"""
Command-line interface
======================
This module provides the CLI entry point and console management
for the Uranus Debian hardening framework.
"""

import click


@click.group()
def cli():
    """Uranus - Debian Hardening Framework."""


def print_error(string: str) -> None:
    """print error messages in red in bold style"""
    click.echo(click.style(f"[ ERROR ] ", fg="red", bold=True), nl=False)
    click.echo(click.style(f"{string}"))
    click.get_text_stream("stderr").flush()


def print_info(string: str):
    """print informational messages in cyan in bold style"""
    click.echo(click.style(f"[ INFO ] ", fg="cyan", bold=True), nl=False)
    click.echo(click.style(f"{string}"))


def format_green(string: str) -> str:
    """return string with green format color in bold style"""
    return click.style(string, fg="green", bold=True)


def format_red(string: str) -> str:
    """return string with red format color in bold style"""
    return click.style(string, fg="red", bold=True)
