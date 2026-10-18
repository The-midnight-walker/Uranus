# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
Parsing Core
============

This file provides parsing utilities.
"""

import configparser
from pathlib import Path

from uranus.shared import SETTINGS as STGS


class Parser:
    CONFIGS = STGS.config

    @staticmethod
    def get_config(pathname: str | Path) -> configparser.ConfigParser:
        """Get a configuration file (.ini).

        Returns:
            The parsed configuration object.

        Raises: FileNotFoundError, configparser.Error.
        """
        config_path = Path(pathname)
        cfg = configparser.ConfigParser()

        with open(config_path, encoding="utf-8") as f:
            cfg.read_file(f)

        return cfg

    @staticmethod
    def parse_whitespace_delimited_config(
        pathname: str | Path,
    ) -> dict[str, str]:
        """Parse whitespace-delimited config file without '=' symbols.

        Supports comments starting with '#' and inline comments.

        Args:
            pathname: Path to the configuration file.

        Returns:
            Dictionary containing configuration key-value pairs.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file contains an invalid or duplicate entry.
        """
        path = Path(pathname)

        if not path.is_file():
            raise FileNotFoundError(path)

        config: dict[str, str] = {}

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Skip comment lines
                if line.startswith("#"):
                    continue

                # Remove inline comments
                if "#" in line:
                    line = line.split("#", 1)[0].strip()

                if not line:
                    continue

                parts = line.split(None, 1)

                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid line {line_number} in {path}: {line!r}"
                    )

                key, value = parts

                if key in config:
                    raise ValueError(
                        f"Duplicate key {key!r} at line {line_number} in {path}"
                    )

                config[key] = value.strip()

        return config
