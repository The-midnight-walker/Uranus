# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import os

PROJECT_NAME = "uranus"
DEBUG_MODE = os.environ.get("DEBUG", "0") == "1"
CONFIG_DIR = os.environ.get("CONFIG_DIR", "./configs/")

# =====================
# DIRECTORIES AND FILES
# =====================

# uranus init file
# TODO: /var/log/uranus.log
CONFIG_FILE_INIT = CONFIG_DIR + "uranus.ini"

# =======
# LOGGING
# =======
# Console logging
ENABLE_CONSOLE_LOGGING = True
DEFAULT_CONSOLE_LOG_LEVEL = "INFO"
DEFAULT_CONSOLE_LOG_COLORED_OUT = True
DEFAULT_CONSOLE_LOG_TIMESTAMP = False
FORMAT_OUTPUT_BOLD = False
# Log file logging
# TODO: Set on True for program logging
ENABLE_FILE_LOGGING = False
DEFAULT_FILE_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE_PATHNAME = PROJECT_NAME + ".log"
DEFAULT_FILE_LOG_TIMESTAMP = True

# ====
# USER
# ====
# Informational messages
INFO_OUTPUT_COLOR = "cyan"
INFO_ENABLE_NL = False  # new line after each message print
INFO_OUTPUT_BOLD = False
INFO_PREFIX = "---| "
# Errors messages
ERROR_OUTPUT_COLOR = "red"
ERROR_ENABLE_NL = False
ERROR_OUTPUT_BOLD = False
ERROR_PREFIX = "[ ERROR ] "
