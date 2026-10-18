# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import logging
import os

from types import SimpleNamespace as sns

# ===============
# PROJECT CONTEXT
# ===============

_debug_mode = os.environ.get("DEBUG", "0") == "1"
_config_dir = os.environ.get("CONFIG_DIR", "credentials.ini")

# Project context
SETTINGS = sns(
    project_name="uranus",
    debug_mode=_debug_mode,
    # Directories and files
    config=sns(
        dir=_config_dir,
        file_init=os.path.join(_config_dir, "uranus.ini"),
        file_cred_init=os.path.join(_config_dir, "credentials.ini"),
        defaults=sns(
            parse=sns(
                int=-1,
                string="None",
            )
        ),
    ),
)
