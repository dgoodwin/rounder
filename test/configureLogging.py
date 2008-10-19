""" Module for configuring test logging. """

__revision__ = "$Revision$"

from rounder.log import setup_logging

import logging


# Configure logging: (needs to be done before importing our modules)
log_conf_locations = ["./logging.conf", "./test/logging.conf",
    "../../test/logging.conf", "../test/logging.conf"]
setup_logging(log_conf_locations)

logger = logging.getLogger("configureLogging")
logger.debug("Configured logging.")
