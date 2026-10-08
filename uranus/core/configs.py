# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import logging
from dataclasses import dataclass
from pathlib import Path
import utils.utils as utils
import utils.shared as shr


@dataclass(slots=True)
class LogConfig:
    console_log_level: int
    file_log_level: int
    log_file: Path
    console_colored_out: bool
    console_log_timestamp: bool
    log_file_timestamp: bool

    @classmethod
    def set_config(cls) -> "LogConfig":
        """Build the LogConfig instance

        Returns:
            The populated LogConfig object

        Raises: FileNotFoundError, configparser.Error, ValueError.
        """

        cfg = utils.get_config()

        # -------- Log file configurations ---------
        file_level_str = cfg.get(
            "logging", "FILE_LOG_LEVEL", fallback=shr.DEFAULT_FILE_LOG_LEVEL
        )

        log_file_timestamp = cfg.getboolean(
            "logging",
            "FILE_LOG_TIMESTAMP",
            fallback=shr.DEFAULT_FILE_LOG_TIMESTAMP,
        )

        # -------- Log console configurations --------
        console_level_str = cfg.get(
            "logging",
            "CONSOLE_LOG_LEVEL",
            fallback=shr.DEFAULT_CONSOLE_LOG_LEVEL,
        )

        console_log_timestamp = cfg.getboolean(
            "logging",
            "CONSOLE_LOG_TIMESTAMP",
            fallback=shr.DEFAULT_CONSOLE_LOG_TIMESTAMP,
        )

        console_colored_out = cfg.getboolean(
            "logging",
            "CONSOLE_LOG_COLORED_OUT",
            fallback=shr.DEFAULT_CONSOLE_LOG_COLORED_OUT,
        )

        # enable debugging mode
        if shr.DEBUG_MODE:
            file_level_str = "DEBUG"
            console_level_str = "DEBUG"

        file_level = logging.getLevelName(file_level_str.upper())
        console_level = logging.getLevelName(console_level_str.upper())

        log_file_path = Path(
            cfg.get(
                "logging",
                "LOGGING_FILE_PATHNAME",
                fallback=shr.DEFAULT_LOG_FILE_PATHNAME,
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
