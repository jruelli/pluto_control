# -*- coding: utf-8 -*-
"""Metadata of package."""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"
__version__ = "0.1.0a1"



# If we are running from a wheel, add the wheel to sys.path
if __package__ == "":
    from os.path import dirname
    from sys import path

    # __file__ is package-*.whl/package/__main__.py
    # Resulting path is the name of the wheel itself
    package_path = dirname(dirname(__file__))
    path.insert(0, package_path)

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2 and "--version" in sys.argv:
        # Catch --version, if this is the only argument (sys.argv[0] is always the script name)
        from __about__ import __version__

        print(__version__)
        sys.exit(0)

    else:
        from pluto_control.pluto_control import main

        # Run the main application of this package
        sys.exit(main())
