# -*- coding: utf-8 -*-
"""Start main application of this package."""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

from . import proginit as pi
from . import __about__
from . import ui_interface
import sys


def main() -> int:
    """Entry point for pluto_control."""
    pi.logger.info("Version: " + __about__.__version__)
    if pi.pargs.gui:
        # Run the main application of this package
        pi.logger.info("Application will run in Windowed mode")
        sys.exit(ui_interface.create_window())
    pi.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
