# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
System Credentials auditing core
================================
Utilities to manage credentials auditing.
"""

from __future__ import annotations

import logging as log

import modules.credentials.convenients as conv
from uranus.core.audits import AuditReport, AuditResult, Severity, AuditItem

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.credentials.units import (
        EtcLoginDefs,
    )


# ---------------
# /etc/login.defs
# ---------------
def do_item_audit(
    report: AuditReport,
    actual: object,
    item: AuditItem,
    compliant: bool,
) -> None:
    """Add an audit result and log non-compliant settings."""
    parameter = next(
        name.upper()
        for name, value in vars(conv.LOGIN_DEFS).items()
        if value is item
    )

    message = (
        f"{parameter} is compliant."
        if compliant
        else item.msg_on_failure.format(current_value=actual)
    )

    if not compliant:
        logger = log.error if item.severity == Severity.CRIT else log.warning
        logger(message)

    report.add_result(
        AuditResult(
            parameter=parameter,
            actual_value=actual,
            expected_value=item.value,
            message=message,
            severity=item.severity,
        ),
        state=compliant,
    )


def login_defs_audit(
    cfg: "EtcLoginDefs.Config",
    report: AuditReport,
) -> AuditReport:
    """Audit /etc/login.defs settings."""

    defs = conv.LOGIN_DEFS

    # ENCRYPT_METHOD

    do_item_audit(
        report,
        cfg.encrypt_method,
        defs.encrypt_method,
        True if str(cfg.encrypt_method) in defs.encrypt_method.value else False,
    )

    # HOME_MODE
    do_item_audit(
        report,
        cfg.home_mode,
        defs.home_mode,
        cfg.home_mode == defs.home_mode.value,
    )

    # UMASK
    do_item_audit(
        report,
        cfg.umask,
        defs.umask,
        True if str(cfg.umask) in defs.umask.value else False,
    )

    # DEFAULT_HOME
    do_item_audit(
        report,
        cfg.default_home,
        defs.default_home,
        cfg.default_home is False
        or (
            isinstance(cfg.default_home, str)
            and cfg.default_home.lower() == str(defs.default_home.value).lower()
        ),
    )

    # PREVENT_NO_AUTH
    do_item_audit(
        report,
        cfg.prevent_no_auth,
        defs.prevent_no_auth,
        isinstance(cfg.prevent_no_auth, str)
        and cfg.prevent_no_auth in {"superuser", "yes"},
    )

    # ENV_PATH
    path = (
        cfg.env_path[5:]
        if isinstance(cfg.env_path, str) and cfg.env_path.startswith("PATH=")
        else cfg.env_path
    )
    elements = path.split(":") if isinstance(path, str) and path else []

    do_item_audit(
        report,
        cfg.env_path,
        defs.env_path,
        bool(elements)
        and all(entry.startswith("/") and entry != "/" for entry in elements),
    )

    # Password aging and login limits
    for actual, item, validate in (
        (
            cfg.passwd_max_days,
            defs.passwd_max_days,
            lambda value, limit: 1 <= value <= limit,
        ),
        (
            cfg.passwd_min_days,
            defs.passwd_min_days,
            lambda value, limit: value >= limit,
        ),
        (
            cfg.login_retries,
            defs.login_retries,
            lambda value, limit: 1 <= value <= limit,
        ),
        (
            cfg.login_timeout,
            defs.login_timeout,
            lambda value, limit: 1 <= value <= limit,
        ),
    ):
        try:
            compliant = validate(int(actual), int(item.value))
        except (TypeError, ValueError):
            compliant = False

        do_item_audit(report, actual, item, compliant)

    # LOG_OK_LOGINS
    do_item_audit(
        report,
        cfg.log_ok_logins,
        defs.log_ok_logins,
        cfg.log_ok_logins is True
        or (
            isinstance(cfg.log_ok_logins, str)
            and cfg.log_ok_logins.lower() in {"yes", "true", "1"}
        ),
    )

    # CHFN_RESTRICT
    do_item_audit(
        report,
        cfg.chfn_restrict,
        defs.chfn_restrict,
        cfg.chfn_restrict == defs.chfn_restrict.value,
    )

    return report
