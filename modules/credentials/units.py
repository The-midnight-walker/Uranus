# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import logging as log
from dataclasses import dataclass
from typing import ClassVar

import modules.credentials.audits as cred_audit
from uranus.core.audits import Audit as AuditCore, AuditReport
from uranus.core.parsers import Parser
from uranus.core.users import User
from uranus.shared import SETTINGS as STGS

_STR_FLBCK = STGS.config.defaults.parse.string
_INT_FLBCK = STGS.config.defaults.parse.int


# ---------------
# /etc/login.defs
# ---------------
class EtcLoginDefs:
    """/etc/login.defs critical security configuration."""

    LOGIN_DEFS_PATHNAME: ClassVar[str] = "/etc/login.defs"

    @dataclass(slots=True, frozen=True)
    class Config:
        log_ok_logins: bool
        umask: str
        home_mode: str
        passwd_max_days: int
        passwd_min_days: int
        login_retries: int
        login_timeout: int
        default_home: bool
        prevent_no_auth: str
        chfn_restrict: str
        encrypt_method: str
        env_path: str

        @classmethod
        def load_config(
            cls,
        ) -> "EtcLoginDefs.Config":
            """Build the UserLoginDefsConfig instance from credentials.ini

            configuration file

            Returns:
                The populated UserLoginDefsConfig object

            Raises: FileNotFoundError, configparser.Error, ValueError.
            """
            try:
                cfg = Parser.get_config(STGS.config.file_cred_init)
            except (FileNotFoundError, ValueError) as err:
                msg = f"On parsing {STGS.config.file_cred_init} : {err}"
                log.error(msg)
                User.print_err(msg)
                raise

            section = "users.login"

            return cls(
                log_ok_logins=cfg.getboolean(
                    section, "LOG_OK_LOGINS", fallback=False
                ),
                umask=cfg.get(section, "UMASK", fallback=_STR_FLBCK).strip(),
                home_mode=cfg.get(
                    section, "HOME_MODE", fallback=_STR_FLBCK
                ).strip(),
                passwd_max_days=cfg.getint(
                    section, "PASS_MAX_DAYS", fallback=_INT_FLBCK
                ),
                passwd_min_days=cfg.getint(
                    section, "PASS_MIN_DAYS", fallback=_INT_FLBCK
                ),
                login_retries=cfg.getint(
                    section, "LOGIN_RETRIES", fallback=_INT_FLBCK
                ),
                login_timeout=cfg.getint(
                    section, "LOGIN_TIMEOUT", fallback=_INT_FLBCK
                ),
                default_home=cfg.getboolean(
                    section, "DEFAULT_HOME", fallback=False
                ),
                prevent_no_auth=cfg.get(
                    section, "PREVENT_NO_AUTH", fallback=_STR_FLBCK
                )
                .strip()
                .lower(),
                chfn_restrict=cfg.get(
                    section, "CHFN_RESTRICT", fallback=_STR_FLBCK
                )
                .strip()
                .lower(),
                encrypt_method=cfg.get(
                    section, "ENCRYPT_METHOD", fallback=_STR_FLBCK
                )
                .strip()
                .upper(),
                env_path=cfg.get(
                    section, "ENV_PATH", fallback=_STR_FLBCK
                ).strip(),
            )

        @classmethod
        def load(
            cls,
        ) -> "EtcLoginDefs.Config":
            """Build the UserLoginDefsConfig instance from /etc/login.defs file.

            Returns:
                The populated UserLoginDefsConfig object.

            Raises:
                FileNotFoundError: If the configuration file does not exist.
                ValueError: If a configuration value has an invalid type or
                            format.
            """
            pathname = EtcLoginDefs.LOGIN_DEFS_PATHNAME
            err_prfx = f"On parsing {pathname} : "

            try:
                cfg = Parser.parse_whitespace_delimited_config(pathname)
                log.debug(f"Parsed file {pathname}.")

                return cls(
                    log_ok_logins=cfg.get("LOG_OK_LOGINS", "no").lower()
                    in {"yes", "true", "1", "on"},
                    umask=cfg.get("UMASK", _STR_FLBCK).strip(),
                    home_mode=cfg.get("HOME_MODE", _STR_FLBCK).strip(),
                    passwd_max_days=int(
                        cfg.get("PASS_MAX_DAYS", str(_INT_FLBCK))
                    ),
                    passwd_min_days=int(
                        cfg.get("PASS_MIN_DAYS", str(_INT_FLBCK))
                    ),
                    login_retries=int(
                        cfg.get("LOGIN_RETRIES", str(_INT_FLBCK))
                    ),
                    login_timeout=int(
                        cfg.get("LOGIN_TIMEOUT", str(_INT_FLBCK))
                    ),
                    default_home=cfg.get("DEFAULT_HOME", "no").lower()
                    in {"yes", "true", "1", "on"},
                    prevent_no_auth=cfg.get("PREVENT_NO_AUTH", _STR_FLBCK)
                    .strip()
                    .lower(),
                    chfn_restrict=cfg.get("CHFN_RESTRICT", _STR_FLBCK)
                    .strip()
                    .lower(),
                    encrypt_method=cfg.get("ENCRYPT_METHOD", _STR_FLBCK)
                    .strip()
                    .upper(),
                    env_path=cfg.get("ENV_PATH", _STR_FLBCK).strip(),
                )

            except (FileNotFoundError, ValueError) as err:
                msg = f"{err_prfx}{err}"
                log.error(msg)
                User.print_err(msg)
                raise
            except Exception as err:
                msg = f"{err_prfx}Unexpected error: {err}"
                log.error(msg)
                User.print_err(msg)
                raise ValueError(msg) from err

    class Audit:
        @classmethod
        def system_audit(cls) -> AuditReport:
            step_fmt = EtcLoginDefs.LOGIN_DEFS_PATHNAME

            report = AuditReport(
                title=step_fmt,
                description=(
                    f"Audit {step_fmt} according to security standards."
                ),
            )

            return AuditCore.run_audit_unit(
                report=report,
                audit_config_fn=EtcLoginDefs.Config.load,
                audit_unit_fn=cred_audit.login_defs_audit,
            )

        @classmethod
        def config_audit(cls) -> AuditReport:
            step_fmt = (
                f"{STGS.config.file_cred_init}::"
                f"[users.login]-(`{EtcLoginDefs.LOGIN_DEFS_PATHNAME}`)"
            )

            report = AuditReport(
                title=step_fmt,
                description=(
                    f"Audit {step_fmt} according to security standards."
                ),
            )

            return AuditCore.run_audit_unit(
                report=report,
                audit_config_fn=(EtcLoginDefs.Config.load_config),
                audit_unit_fn=cred_audit.login_defs_audit,
            )
