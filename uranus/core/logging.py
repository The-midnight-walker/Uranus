# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
Logging core
============
Manages dual-handler logging output (console stdout and log file)
"""

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from types import SimpleNamespace as sns
from typing import Any, ClassVar

import click

from uranus.core.parsers import Parser
from uranus.core.users import User
from uranus.shared import SETTINGS as STGS


@dataclass(slots=True)
class LogConfig:
    console_log_level: int
    file_log_level: int
    log_file: Path
    console_colored_out: bool
    console_log_timestamp: bool
    log_file_timestamp: bool

    LOG_LEVELS: ClassVar[dict[int, dict[str, Any]]] = {
        logging.DEBUG: {
            "label": "DEBUG",
            "style": {"fg": "bright_black", "bold": False},
        },
        logging.INFO: {
            "label": "INFO",
            "style": {"fg": "green", "bold": False},
        },
        logging.WARNING: {
            "label": "WARN",
            "style": {"fg": "yellow", "bold": False},
        },
        logging.ERROR: {
            "label": "ERROR",
            "style": {"fg": "red", "bold": False},
        },
        logging.CRITICAL: {
            "label": "CRIT",
            "style": {"fg": "bright_red", "bold": False},
        },
    }

    CONSOLE = sns(
        enable=False,
        default_level="INFO",
        log_timestamp=True,
        output=sns(
            bold=False,
            enable_color=True,
            timestamp_color="yellow",
            meta_color="green",
        ),
    )

    LOG_FILE = sns(
        enable=True,
        default_level="INFO",
        pathname=STGS.project_name + ".log",
        log_timestamp=True,
    )

    class Formatter(logging.Formatter):
        """Formatter supporting optional terminal colors."""

        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        ENABLE_COLOR = False

        def __init__(
            self,
            fmt: str | None = None,
            datefmt: str | None = None,
            *,
            enable_color: bool = False,
        ) -> None:
            super().__init__(fmt=fmt, datefmt=datefmt)
            self.enabled_color = enable_color

        @classmethod
        def configure(
            cls,
            enable_color: bool | None = None,
            date_format: str | None = None,
        ) -> None:
            """Configure global formatting preferences."""

            if enable_color is not None:
                cls.ENABLE_COLOR = enable_color

            if date_format is not None:
                cls.DATE_FORMAT = date_format

        def format(self, record: logging.LogRecord) -> str:
            colored = self.enabled_color
            padded_level = f"{record.levelname:<5s}"

            style_args = LogConfig.LOG_LEVELS.get(record.levelno, {}).get(
                "style", {}
            )

            if colored and style_args:
                padded_level = click.style(
                    padded_level,
                    **style_args,
                )

            parts = [f"[ {padded_level} ]"]

            if self.usesTime():
                asctime = self.formatTime(record, self.datefmt)
                time_str = f"[ {asctime} ]"

                if colored:
                    time_str = click.style(
                        time_str,
                        fg=LogConfig.CONSOLE.output.timestamp_color,
                    )

                parts.append(time_str)

            if record.name:
                module_content = f"module={record.name}"

                if STGS.debug_mode and record.pathname and record.lineno:
                    try:
                        file_path = Path(record.pathname).relative_to(
                            Path.cwd()
                        )
                    except ValueError:
                        file_path = record.pathname

                    module_content += f", {file_path}:{record.lineno}"

                meta_str = f"[ {module_content} ]"

                if colored:
                    meta_str = click.style(
                        meta_str,
                        fg=LogConfig.CONSOLE.output.meta_color,
                    )

                parts.append(meta_str)

            parts.append(record.getMessage())

            return " ".join(parts)

        @classmethod
        def get_file_log_formatter(
            cls,
            cfg: "LogConfig",
        ) -> logging.Formatter:
            """Create the file log formatter."""

            log_format = "[ %(levelname)-5s ]"

            if cfg.log_file_timestamp:
                log_format += " [ %(asctime)s ]"

            log_format += " [ module=%(name)s"

            if STGS.debug_mode:
                log_format += ", %(pathname)s:%(lineno)d"

            log_format += " ] %(message)s"

            return logging.Formatter(
                fmt=log_format,
                datefmt=(cls.DATE_FORMAT if cfg.log_file_timestamp else None),
            )

        @classmethod
        def get_console_log_formatter(
            cls,
            cfg: "LogConfig",
        ) -> logging.Formatter:
            """Create the console log formatter."""

            log_format = "[ %(levelname)-5s ]"

            if cfg.console_log_timestamp:
                log_format += " [ %(asctime)s ]"

            log_format += " [ module=%(name)s"

            if STGS.debug_mode:
                log_format += ", %(pathname)s:%(lineno)d"

            log_format += " ] %(message)s"

            return cls(
                fmt=log_format,
                datefmt=(
                    cls.DATE_FORMAT if cfg.console_log_timestamp else None
                ),
                enable_color=cfg.console_colored_out,
            )

    @classmethod
    def set_config(cls) -> "LogConfig":
        """Build the LogConfig instance

        Returns:
            The populated LogConfig object

        Raises: FileNotFoundError, configparser.Error, ValueError.
        """
        try:
            cfg = Parser.get_config(STGS.config.file_init)
        except Exception as err:
            msg = f"On parsing {STGS.config.file_init} : {err}"
            User.print_err(msg)
            raise

        # -------- Log file configurations ---------
        file_level_str = cfg.get(
            "logging",
            "FILE_LOG_LEVEL",
            fallback=cls.LOG_FILE.default_level,
        )

        log_file_timestamp = cfg.getboolean(
            "logging",
            "FILE_LOG_TIMESTAMP",
            fallback=cls.LOG_FILE.log_timestamp,
        )

        # -------- Log console configurations --------
        console_level_str = cfg.get(
            "logging",
            "CONSOLE_LOG_LEVEL",
            fallback=cls.CONSOLE.default_level,
        )

        console_log_timestamp = cfg.getboolean(
            "logging",
            "CONSOLE_LOG_TIMESTAMP",
            fallback=cls.CONSOLE.log_timestamp,
        )

        console_colored_out = cfg.getboolean(
            "logging",
            "CONSOLE_LOG_COLORED_OUT",
            fallback=cls.CONSOLE.output.enable_color,
        )

        # enable debugging mode
        if STGS.debug_mode:
            file_level_str = "DEBUG"
            console_level_str = "DEBUG"

        file_level = cls._resolve_log_level(
            file_level_str,
            cls.LOG_FILE.default_level,
        )
        console_level = cls._resolve_log_level(
            console_level_str,
            cls.CONSOLE.default_level,
        )

        log_file_path = Path(
            cfg.get(
                "logging",
                "LOGGING_FILE_PATHNAME",
                fallback=cls.LOG_FILE.pathname,
            )
        )

        return cls(
            console_log_level=console_level,
            file_log_level=file_level,
            log_file=log_file_path,
            log_file_timestamp=log_file_timestamp,
            console_colored_out=console_colored_out,
            console_log_timestamp=console_log_timestamp,
        )

    @classmethod
    def print_log_file(
        cls,
        file_path: str,
        colored: bool = True,
    ) -> None:
        """Read a raw log file and reapply the console printing format
        and colors as ClickColoredFormatter for console output.
        """
        path = Path(file_path)

        if not path.exists():
            User.print_err(f"Log file not found: {file_path}")
            return

        # Regular expression to capture blocks of your log format:
        # [ LEVEL ] [ ASYNC_TIME ] [ MODULE_INFO ] MESSAGE
        log_pattern = re.compile(
            r"^\[\s*(?P<level>\w+)\s*\]"
            r"(?:\s*\[\s*(?P<time>\d{4}-\d{2}-\d{2}[^\]]*?)\s*\])?"
            r"(?:\s*\[\s*(?P<meta>[^\]]+?)\s*\])?"
            r"\s+(?P<message>.*)$"
        )

        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip()

                    if not line:
                        continue

                    match = log_pattern.match(line)

                    if not match:
                        # Fallback: print raw line if format does not match
                        click.echo(line)
                        continue

                    data = match.groupdict()
                    parts = []

                    level_str = f"{data['level']:<5s}"
                    level_info = next(
                        (
                            info
                            for info in cls.LOG_LEVELS.values()
                            if info["label"] == data["level"]
                        ),
                        {},
                    )
                    style_args = level_info.get("style", {})

                    if colored and style_args:
                        colored_level = click.style(
                            level_str,
                            **style_args,
                        )
                    else:
                        colored_level = level_str

                    parts.append(f"[ {colored_level} ]")

                    if data["time"]:
                        time_str = f"[ {data['time']} ]"

                        if colored:
                            time_str = click.style(
                                time_str,
                                fg=cls.CONSOLE.output.timestamp_color,
                            )

                        parts.append(time_str)

                    if data["meta"]:
                        meta_str = f"[ {data['meta']} ]"

                        if colored:
                            meta_str = click.style(
                                meta_str,
                                fg=cls.CONSOLE.output.meta_color,
                            )

                        parts.append(meta_str)

                    parts.append(data["message"])
                    click.echo(" ".join(parts))

        except OSError as err:
            User.print_err(f"Unable to read log file {file_path}: {err}")

    @classmethod
    def init_logging(cls) -> None:
        """Initialize the dual logging system (console + log file) globally."""

        # redefine personal levelnames
        for level, info in cls.LOG_LEVELS.items():
            logging.addLevelName(level, info["label"])

        log_cfg = cls.set_config()
        cls._setup_logging(log_cfg)

    @staticmethod
    def _resolve_log_level(
        level_name: str,
        fallback_level_name: str,
    ) -> int:
        """Safely convert a log level name to an integer logging level."""
        lvl = logging.getLevelName(level_name.upper())

        if isinstance(lvl, int):
            return lvl

        fallback = logging.getLevelName(fallback_level_name.upper())

        if isinstance(fallback, int):
            return fallback

        return logging.INFO

    @classmethod
    def _setup_logging(cls, cfg: "LogConfig") -> logging.Logger:
        """Configure dual logging output to both console and a log file.

        Args:
            cfg: LogConfig dataclass instance.

        Returns:
            The configured root logger instance.
        """
        logger = logging.getLogger()
        logger.setLevel(min(cfg.console_log_level, cfg.file_log_level))

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        if cls.CONSOLE.enable:
            console_formatter = cls.Formatter.get_console_log_formatter(cfg=cfg)

            # --- Console Handler ---
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(cfg.console_log_level)
            stream_handler.setFormatter(console_formatter)
            logger.addHandler(stream_handler)

        if cls.LOG_FILE.enable:
            file_formatter = cls.Formatter.get_file_log_formatter(cfg=cfg)

            # File Handler
            file_handler = logging.FileHandler(
                cfg.log_file,
                encoding="utf-8",
            )
            file_handler.setLevel(cfg.file_log_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        if not cls.CONSOLE.enable and not cls.LOG_FILE.enable:
            logger.addHandler(logging.NullHandler())

        return logger
