# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

import logging

from uranus.core.logging import LogConfig
from uranus.core.module import cli

logger = logging.getLogger(__name__)


def main() -> None:
    # init the logging feature
    LogConfig.init_logging()

    # launch the command line
    cli()


if __name__ == "__main__":
    main()
