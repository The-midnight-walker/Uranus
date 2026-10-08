# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
Logging core
============
Manages dual-handler logging output (console stdout and log file)
"""

import logging
from pathlib import Path
from uranus.core.configs import LogConfig
from utils.formats import ClickColoredFormatter
import utils.shared as shr


def init_logging() -> None:
    """
    Initialize the dual logging system (console + log file) globally.
    """

    # redefine personal levelnames
    logging.addLevelName(logging.DEBUG, "DEBUG")
    logging.addLevelName(logging.INFO, "INFO")
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.ERROR, "ERROR")
    logging.addLevelName(logging.CRITICAL, "FATAL")

    log_cfg = LogConfig.set_config()
    _setup_logging(log_cfg)


def _setup_logging(cfg: LogConfig) -> logging.Logger:
    """Configure dual logging output to both console and a log file.

    Args:
        cfg: LogConfig dataclass instance.

    Returns:
        The configured root logger instance.
    """

    logger = logging.getLogger()
    logger.setLevel(min(cfg.console_log_level, cfg.file_log_level))

    if logger.hasHandlers():
        logger.handlers.clear()

    date_format = "%Y-%m-%d %H:%M:%S"

    if shr.ENABLE_CONSOLE_LOGGING:
        # --- Format for the console ---
        console_log_format = "[ %(levelname)-5s ]"
        if cfg.console_log_timestamp:
            console_log_format += " [ %(asctime)s ]"
        if shr.DEBUG_MODE:
            console_log_format += " [ %(name)s:%(lineno)d ]"
        console_log_format += " %(message)s"

        # --- Console Handler ---
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(cfg.console_log_level)
        console_formatter = ClickColoredFormatter(
            fmt=console_log_format,
            datefmt=date_format if cfg.console_log_timestamp else None,
        )
        console_formatter.enabled_color = cfg.console_colored_out

        stream_handler.setFormatter(console_formatter)
        logger.addHandler(stream_handler)

    if shr.ENABLE_FILE_LOGGING:
        # --- Format for the log file ---
        file_log_format = "[ %(levelname)-5s ]"
        if cfg.log_file_timestamp:
            file_log_format += " [ %(asctime)s ]"
        if shr.DEBUG_MODE:
            file_log_format += " [ %(name)s:%(lineno)d ]"
        file_log_format += " %(message)s"

        file_formatter = logging.Formatter(
            fmt=file_log_format,
            datefmt=date_format if cfg.log_file_timestamp else "",
        )

        # File Handler
        file_handler = logging.FileHandler(cfg.log_file, encoding="utf-8")
        file_handler.setLevel(cfg.file_log_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
