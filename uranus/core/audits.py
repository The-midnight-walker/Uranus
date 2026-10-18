# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import time
import click
import logging as log
from typing import Any
from collections.abc import Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering

from uranus.core.users import User


@total_ordering
class Severity(Enum):
    CRIT = (4, "C", "CRITICAL")
    HIGH = (3, "H", "HIGH")
    MED = (2, "M", "MEDIUM")
    LOW = (1, "L", "LOW")

    @property
    def level(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]

    @property
    def label(self):
        return self.value[2]

    def __lt__(self, other):
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level < other.level

    def __eq__(self, other):
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level == other.level


class AuditStatus:
    PASS = "SUCCEED"
    FAIL = "FAILED"


@dataclass(slots=True)
class AuditResult:
    """Represents the detailed result of an individual configuration test.

    `status` is True when the test passed, False when it failed.
    """

    parameter: str
    actual_value: Any
    expected_value: Any
    message: str
    severity: Severity
    status: bool = False


@dataclass(slots=True)
class AuditReport:
    """Represents the global report for an audit step or module."""

    title: str
    description: str
    report: list[AuditResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    severity: Severity = field(default_factory=lambda: Severity.CRIT)

    def add_result(self, result: AuditResult, state: bool) -> None:
        """Record a test result; `state` is True if the test passed."""
        result.status = bool(state)
        self.report.append(result)

    def print_results(self, results: list[AuditResult]) -> None:
        for res in results:
            prefix = (
                User.Formatter.format(
                    res.severity.code,
                    fg="bright_black",
                )
                + "  "
                if User.VERBOSE
                else ""
            )

            if not res.status:  # Failed
                message = f"{prefix}{res.message}"

                if res.severity.level <= self.severity.level:
                    User.print_err(message)
                else:
                    User.print_warn(message)

            elif User.VERBOSE:
                pass_prefix = User.Formatter.format(
                    "[ PASS  ]",
                    fg="bright_green",
                )
                User.print_success(f"{pass_prefix} {prefix}{res.message}")

    @property
    def is_compliant(self) -> str:
        """Returns AuditStatus.PASS unless a HIGH/CRITICAL test failed,
        in which case AuditStatus.FAIL is returned.
        """
        blocking = any(
            not r.status and r.severity.level <= self.severity.level
            for r in self.report
        )
        return AuditStatus.FAIL if blocking else AuditStatus.PASS

    def report_stats_str(self, report: list[AuditResult]) -> str:
        if not report:
            return ""

        counts = {sev.code: 0 for sev in Severity}

        for r in report:
            if r.severity in Severity:
                counts[r.severity.code] += 1

        return "   ".join(
            f"{sev.code} ({counts[sev.code]})"
            for sev in Severity
            if counts[sev.code] > 0
        )

    @property
    def issues(self) -> list[AuditResult]:
        """Returns only the failed tests."""
        return [r for r in self.report if not r.status]

    @property
    def passed(self) -> list[AuditResult]:
        """Returns only the passed tests."""
        return [r for r in self.report if r.status]

    def print_report(self):
        """Process all collected audit reports at the end of the run."""
        if not self.report:
            return

        status = self.is_compliant

        User.print(User.Formatter.format(self.title, fg="cyan"))

        # User.print_info is already print only in Verbose Mode
        # then its a little bit redundant certainly
        if User.VERBOSE:
            timestamp = datetime.fromtimestamp(self.timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            User.print_info(
                f"{User.Formatter.format('Timestamp:', fg='green')} {timestamp}"
            )
            User.print_info(
                User.Formatter.format("Description: ", fg="green")
                + self.description
            )
            User.print_info(
                User.Formatter.format("Checked: ", fg="green")
                + self.report_stats_str(report=self.report)
            )
            User.print_info(
                User.Formatter.format("Passed:  ", fg="green")
                + self.report_stats_str(self.passed)
            )
            User.print_info(
                User.Formatter.format("Failed:  ", fg="green")
                + self.report_stats_str(self.issues)
            )
            User.print_info(
                User.Formatter.format("Status:  ", fg="green") + status
            )

        else:
            if status == AuditStatus.PASS:
                status_label = User.Formatter.format(
                    "Status: ",
                    fg="green",
                )
                status_value = User.Formatter.format(
                    status,
                    fg=User.OUTPUT_FORMATS.success.color,
                )
                issue_count = User.Formatter.format(
                    len(self.issues),
                    fg=User.OUTPUT_FORMATS.failure.color,
                )

                User.print_success(
                    f"{status_label}'{status_value}' ",
                    nl=False,
                )
                User.print_success(f"with ({issue_count}) warning(s)")

            else:
                status_label = User.Formatter.format(
                    "Status: ",
                    fg="green",
                )
                status_value = User.Formatter.format(
                    status,
                    fg=User.OUTPUT_FORMATS.failure.color,
                )
                issue_count = User.Formatter.format(
                    len(self.issues),
                    fg=User.OUTPUT_FORMATS.failure.color,
                )

                User.print_failure(
                    f"{status_label}'{status_value}' ",
                    nl=False,
                )
                User.print_failure(f"with ({issue_count}) issue(s)")

        self.print_results(self.report)


@dataclass
class AuditItem:
    value: object
    severity: Severity
    msg_on_failure: str  # Use {0}...{n} for the actual value if it need
    # to be print


class Audit:
    @staticmethod
    def export_audits(
        ctx: click.Context,
        reports: list[AuditReport],
    ) -> None:
        """Export audit reports or print them to the terminal."""

        output_opts = ctx.obj.get("audit", {}).get("output", {})
        export_path = output_opts.get("export_path")
        output_format = output_opts.get("output_format", "txt")

        # TODO:
        def _export_audit_reports_json(reports: list[AuditReport]):
            pass

        def _export_audit_reports_yaml(reports: list[AuditReport]):
            pass

        def _export_audit_reports_xml(reports: list[AuditReport]):
            pass

        def _export_audit_reports_txt(reports: list[AuditReport]):
            pass

        if not export_path:
            Audit.print_audits(reports=reports)
            return

        exporters = {
            "json": _export_audit_reports_json,
            "yaml": _export_audit_reports_yaml,
            "xml": _export_audit_reports_xml,
            "txt": _export_audit_reports_txt,
        }

        exporter = exporters.get(output_format)
        if exporter is None:
            raise click.ClickException(
                f"Unsupported export format: {output_format}"
            )

        content = exporter(reports=reports)

        try:
            with open(export_path, "w", encoding="utf-8", newline="\n") as file:
                file.write(content)
        except OSError as err:
            raise click.ClickException(
                f"Cannot export audit reports to '{export_path}': {err}"
            ) from err

        click.echo(
            f"Audit reports exported to {export_path} ({output_format})",
            err=True,
        )

    @staticmethod
    def print_audits(
        reports: list[AuditReport] | None = None,
    ) -> None:
        """Process all collected audit reports at the end of the run."""
        if reports is None:
            return

        total_reports = len(reports)
        if User.VERBOSE:
            User.print(
                User.Formatter.format(
                    "+--------------------+", fg="bright_black"
                )
            )
            User.print(
                User.Formatter.format(
                    "+   AUDITS REPORTS   +", fg="bright_black"
                )
            )
            User.print(
                User.Formatter.format(
                    "+--------------------+", fg="bright_black"
                )
            )

            User.print(
                User.Formatter.format(
                    "Security levels: [ L: Low | M: Medium "
                    "| H: High | C: Critical ]\n",
                    fg="bright_black",
                )
            )

        for idx, report in enumerate(reports, start=1):
            User.print(
                User.Formatter.format(
                    f"[ {idx}/{total_reports} ] ", fg="bright_black"
                ),
                nl=False,
            )
            report.print_report()
            User.print("")

    @classmethod
    def run_audit_unit(
        cls,
        report: AuditReport,
        audit_config_fn: Callable[[], Any],
        audit_unit_fn: Callable[[Any, AuditReport], AuditReport],
    ) -> AuditReport:
        """Executes a single audit unit safely, handling configuration loading
        and exception catching without crashing the whole application.
        """

        def _complete_audit_unit(report: AuditReport) -> AuditReport:
            """
            Record completed unit report and print verbose status if enabled.
            """

            status = report.is_compliant
            logfmt = (
                f"{report.title} ends on '{status}' status with "
                f"{len(report.issues)} issue(s)"
            )

            if status == AuditStatus.FAIL:
                log.warning(logfmt)
            else:
                log.info(logfmt)

            return report

        try:
            User.print_info(report.title, nl=False)
            log.debug(f"Audit file {report.title}")

            cfg = audit_config_fn()
            report = audit_unit_fn(cfg, report)

            # Little tips
            User.print_info("." * max(3, len(report.title) // 15) + "DONE.")

            return _complete_audit_unit(report=report)

        except Exception as err:
            msg = f"On auditing {report.title}: {err}"
            log.error(msg)
            User.print_err(msg)
            report.add_result(
                AuditResult(
                    parameter="CONFIGURATION_LOAD",
                    actual_value=str(err),
                    expected_value="Valid configuration",
                    message=msg,
                    severity=Severity.CRIT,
                ),
                state=False,
            )
            return _complete_audit_unit(report=report)

    @classmethod
    def do_audit(
        cls,
        ctx: click.Context,
        sys_units: list,
        cfg_units: list,
    ) -> None:
        """Do audit"""
        audit_ctx = ctx.obj.get("audit", {})
        units = list()
        system = audit_ctx.get("system", False)
        config = audit_ctx.get("config", False)

        def _execute_audit(
            units: Callable[[], AuditReport] | list[Callable[[], AuditReport]],
        ) -> list[AuditReport]:
            """
            Run audit unit(s) sequentially and return the collected reports.
            """
            if callable(units):
                units = [units]

            reports: list[AuditReport] = []
            total_units = len(units)

            for idx, unit in enumerate(units, start=1):
                User.print_info(f"[ {idx}/{total_units} ] ", nl=False)
                rep = unit()
                if isinstance(rep, AuditReport):
                    reports.append(rep)

            return reports

        log.debug(
            f"Auditing login-defs entity for system:={system}, config:={config}"
        )

        if system:
            units.extend(sys_units)

        if config:
            units.extend(cfg_units)

        reports = _execute_audit(units=units)
        cls.export_audits(ctx=ctx, reports=reports)
