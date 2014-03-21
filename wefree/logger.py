"""Logging set up."""

import logging
import os
import sys
import traceback

from logging.handlers import RotatingFileHandler

import xdg.BaseDirectory


class CustomRotatingFH(RotatingFileHandler):
    """Rotating handler that starts a new file for every run."""

    def __init__(self, *args, **kwargs):
        RotatingFileHandler.__init__(self, *args, **kwargs)
        self.doRollover()


def exception_handler(exc_type, exc_value, tb):
    """Handle an unhandled exception."""
    exception = traceback.format_exception(exc_type, exc_value, tb)
    msg = "".join(exception)
    print >> sys.stderr, msg

    # log
    logger = logging.getLogger('wefree')
    logger.error("Unhandled exception!\n%s", msg)


def get_filename():
    """Return the log file name."""
    return os.path.join(xdg.BaseDirectory.xdg_cache_home,
                        'wefree', 'wefree.log')


def set_up(verbose):
    """Set up the logging."""

    logfile = get_filename()
    print "Saving logs to", repr(logfile)
    logfolder = os.path.dirname(logfile)
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)

    logger = logging.getLogger('wefree')
    handler = CustomRotatingFH(logfile, maxBytes=1e6, backupCount=10)
    logger.addHandler(handler)
    formatter = logging.Formatter("%(asctime)s  %(name)-22s  "
                                  "%(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)

    if verbose:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)

    # hook the exception handler
    sys.excepthook = exception_handler
