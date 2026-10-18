# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""Hardening definitions and baseline security parameters for credentials.

Credits:
    https://wiki.farnetiandrea.it/operating-systems/linux/deploy/linux-hardening
"""

from types import SimpleNamespace as sns

from uranus.core.audits import AuditItem, Severity


LOGIN_DEFS = sns(
    log_ok_logins=AuditItem(
        value="yes",
        severity=Severity.HIGH,
        msg_on_failure="LOG_OK_LOGINS is '{current_value}', expected 'yes'.",
    ),
    umask=AuditItem(
        value={"027", "077"},
        severity=Severity.CRIT,
        msg_on_failure=(
            "UMASK is '{current_value}', expected a mask at least as "
            "restrictive as one of ['027', '077']."
        ),
    ),
    home_mode=AuditItem(
        value="0700",
        severity=Severity.CRIT,
        msg_on_failure="HOME_MODE is '{current_value}', expected '0700'.",
    ),
    passwd_max_days=AuditItem(
        value="90",
        severity=Severity.HIGH,
        msg_on_failure="PASS_MAX_DAYS is '{current_value}'"
        ", expected a value between 1 and 90.",
    ),
    passwd_min_days=AuditItem(
        value="1",
        severity=Severity.HIGH,
        msg_on_failure="PASS_MIN_DAYS is '{current_value}',"
        " expected at least 1.",
    ),
    login_retries=AuditItem(
        value="3",
        severity=Severity.HIGH,
        msg_on_failure="LOGIN_RETRIES is '{current_value}',"
        " expected a value between 1 and 3.",
    ),
    login_timeout=AuditItem(
        value="30",
        severity=Severity.MED,
        msg_on_failure="LOGIN_TIMEOUT is '{current_value}',"
        " expected a value between 1 and 30.",
    ),
    default_home=AuditItem(
        value="no",
        severity=Severity.CRIT,
        msg_on_failure="DEFAULT_HOME is '{current_value}', expected 'no'.",
    ),
    prevent_no_auth=AuditItem(
        value="superuser",
        severity=Severity.CRIT,
        msg_on_failure=(
            "PREVENT_NO_AUTH is '{current_value}',"
            " expected 'superuser' or 'yes'."
        ),
    ),
    chfn_restrict=AuditItem(
        value="rwh",
        severity=Severity.MED,
        msg_on_failure="CHFN_RESTRICT is '{current_value}', expected 'rwh'.",
    ),
    encrypt_method=AuditItem(
        value={"YESCRYPT"},
        severity=Severity.CRIT,
        msg_on_failure="ENCRYPT_METHOD is '{current_value}'"
        " expected [ YESCRYPT ].",
    ),
    env_path=AuditItem(
        value="PATH=/usr/local/bin:/usr/bin:/bin",
        severity=Severity.CRIT,
        msg_on_failure="ENV_PATH '{current_value}' contains relative, empty"
        ", or unsafe directory entries.",
    ),
)
