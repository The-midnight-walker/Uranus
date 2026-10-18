# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import logging as log

import click

import modules.credentials.units as creds
from uranus.core.audits import Audit


@click.group(name="cred")
@click.pass_context
def cred(ctx: click.Context) -> None:
    """Manage user credentials and account security policies.

    Provides commands to audit, enforce, and harden local user account
    configurations, password policies, and authentication mechanisms on Debian
    platforms.
    """
    ctx.ensure_object(dict)


@cred.group(name="audit")
@click.option(
    "-c",
    "--config",
    is_flag=True,
    help="Audit current credentials configuration file",
)
@click.option(
    "-e",
    "--export",
    type=click.Path(writable=True, path_type=str),
    help="Save output in a file with the chosen format.",
)
@click.option(
    "--format",
    type=click.Choice(["yaml", "xml", "json", "txt"], case_sensitive=False),
    default="txt",
    help="Output format (yaml, xml, json, txt).",
)
@click.option(
    "-s",
    "--system",
    is_flag=True,
    help="Audit system files about users credentials",
)
@click.pass_context
def audit(
    ctx: click.Context,
    config: bool,
    system: bool,
    export: str | None,
    format: str,
) -> None:
    """Audit user credentials components."""
    # TODO: verify if user have the SYS_ADMIN capability (root)
    log.debug("Auditing credentials group")

    ctx.ensure_object(dict)

    # Fallback
    if not system and not config:
        system = True
        config = True

    ctx.obj.update(
        audit={
            "system": system,
            "config": config,
            "output": {
                "export_path": export,
                "output_format": format.lower(),
            },
        }
    )


@audit.command(name="all")
@click.pass_context
def all_audit(ctx: click.Context) -> None:
    """Audit all configurations."""
    Audit.do_audit(
        ctx=ctx,
        sys_units=[creds.EtcLoginDefs.Audit.system_audit],
        cfg_units=[creds.EtcLoginDefs.Audit.config_audit],
    )


@audit.command(name="login-defs")
@click.pass_context
def login_defs_audit(ctx: click.Context) -> None:
    """Audit login.defs configurations."""
    Audit.do_audit(
        ctx=ctx,
        sys_units=[creds.EtcLoginDefs.Audit.system_audit],
        cfg_units=[creds.EtcLoginDefs.Audit.config_audit],
    )
