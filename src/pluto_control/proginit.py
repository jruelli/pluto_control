# -*- coding: utf-8 -*-
"""Global program initialization."""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import logging
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from os import R_OK, W_OK, access, remove
from os.path import abspath, dirname, exists, join
from shutil import copy, move

programname = "pluto_control"  # Program name

conf_rw = False  # If you want so save the configuration with .save_conf() set to True
conf_rw_save = False  # Create new conf file in same directory and move to old one
conf_rw_backup = False  # Keep a backup of old conf file [filename].bak

conf = ConfigParser()
logger = logging.getLogger()
pidfile = "/run/{0}.pid".format(programname)


def cleanup():
    """Clean up program."""
    # Shutdown logging system
    logging.shutdown()


def reconfigure_logger():
    """Configure logging module of program."""

    # Clear all log handler
    for lhandler in logger.handlers.copy():
        lhandler.close()
        logger.removeHandler(lhandler)

    # Create new log handler
    logformat = logging.Formatter("{asctime} [{levelname:8}] {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")
    lhandler = logging.StreamHandler(sys.stdout)
    lhandler.setFormatter(logformat)
    logger.addHandler(lhandler)

    if "logfile" in pargs and pargs.logfile is not None:
        # Write logs to a logfile
        lhandler = logging.FileHandler(filename=pargs.logfile)
        lhandler.setFormatter(logformat)
        logger.addHandler(lhandler)

    # Loglevel auswerten
    if pargs.verbose == 1:
        loglevel = logging.INFO
    elif pargs.verbose > 1:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    logger.setLevel(loglevel)


def reload_conf(clear_load=False) -> None:
    """
    Reload config file.

    If keys are commented out in conf file, they will still be in the conf file.
    To remove not existing keys set clear_load to True.

    :param clear_load: Clear conf before reload
    """
    if "conffile" in pargs:
        # Check config file
        if not access(pargs.conffile, R_OK):
            raise RuntimeError("can not access config file '{0}'".format(pargs.conffile))
        if conf_rw:
            if (conf_rw_save or conf_rw_backup) and not access(dirname(pargs.conffile), W_OK):
                raise RuntimeError(
                    "can not write to directory '{0}' to create files" "".format(dirname(pargs.conffile))
                )
            if not access(pargs.conffile, W_OK):
                raise RuntimeError("can not write to config file '{0}'".format(pargs.conffile))

        if clear_load:
            # Clear all sections and do not create a new instance
            for section in conf.sections():
                conf.remove_section(section)

        # Read configuration
        logger.info("loading config file: {0}".format(pargs.conffile))
        conf.read(pargs.conffile)


def save_conf():
    """Save configuration."""
    if not conf_rw:
        raise RuntimeError("You have to set conf_rw to True.")
    if "conffile" in pargs:
        if conf_rw_backup:
            copy(pargs.conffile, pargs.conffile + ".bak")
        if conf_rw_save:
            with open(pargs.conffile + ".new", "w") as fh:
                conf.write(fh)
            move(pargs.conffile + ".new", pargs.conffile)
        else:
            with open(pargs.conffile, "w") as fh:
                conf.write(fh)


# Generate command arguments of the program
parser = ArgumentParser(prog=programname, description="Program description")
parser.add_argument("-n", "--no-gui", action="store_false", default="true", dest="gui", help="Run program without GUI")
parser.add_argument(
    "-c", "--conffile", dest="conffile", default="{0}.conf".format(programname), help="Application configuration file"
)
parser.add_argument("-f", "--logfile", dest="logfile", help="Save log entries to this file")

parser.add_argument("-v", "--verbose", action="count", dest="verbose", default=0, help="Switch on verbose logging")
pargs = parser.parse_args()

# Check important objects and set to default if they do not exist
if "verbose" not in pargs:
    pargs.verbose = 0

# Get absolute paths
pwd = abspath(".")

# Configure logger
if "logfile" in pargs and pargs.logfile is not None and dirname(pargs.logfile) == "":
    pargs.logfile = join(pwd, pargs.logfile)
reconfigure_logger()

# Initialize configparser of globalconfig
if "conffile" in pargs and dirname(pargs.conffile) == "":
    pargs.conffile = join(pwd, pargs.conffile)


# Load configuration - Comment out, if you do that in your own program
reload_conf()
