# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
ROOT/CORE MODULE & CLI UTILITIES INITIALIZATION
===============================================

Provide the main entry point and his configurations for the application,
handling global CLI options such as verbosity and color output, and
initializing the execution context.
"""

import logging as log

import click

from modules.credentials.module import cred
from uranus.core.users import User


@click.group(name="root", invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Increase output verbosity",
)
@click.option(
    "-c",
    "--color",
    is_flag=True,
    help="Colored command line output text",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, color: bool) -> None:
    """
    \b
        ██╗   ██╗ ██████╗   █████╗  ███╗   ██╗ ██╗   ██╗ ███████╗
        ██║   ██║ ██╔══██╗ ██╔══██╗ ████╗  ██║ ██║   ██║ ██╔════╝
        ██║   ██║ ██████╔╝ ███████║ ██╔██╗ ██║ ██║   ██║ ███████╗
        ██║   ██║ ██╔══██╗ ██╔══██║ ██║╚██╗██║ ██║   ██║ ╚════██║
        ╚██████╔╝ ██║  ██║ ██║  ██║ ██║ ╚████║ ╚██████╔╝ ███████║
         ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝  ╚═════╝  ╚══════╝

    A scripting framework for hardening GNU/Linux Debian (13 - Trixie)
    distribution
    """

    ctx.ensure_object(dict)

    log.debug(
        f"Initialize the CLI context [ color={color}, verbose={verbose} ]"
    )

    # Configure User's prints
    User.configure(colored=color, verbose=verbose)

    ctx.obj["COLOR"] = color
    ctx.obj["VERBOSE"] = verbose

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# =================================
# REGISTERING SUB-COMMANDS & GROUPS
# =================================
cli.add_command(cred)
