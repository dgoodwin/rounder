""" Utility functions related to logging. """

__revision__ = "$Revision$"

import logging
import logging.config
from os.path import expanduser, exists, abspath

def setup_logging(conf_file_locations):
    """ Configure logging by searching for a logging configuration file
    in the provided list of locations. If none are found, default to no
    logging.
    """
    actual_log_conf_location = None
    for location in conf_file_locations:
        if exists(expanduser(location)):
            actual_log_conf_location = location
            break

    if actual_log_conf_location != None:
        logging.config.fileConfig(expanduser(location))
    else:
        print("Unable to locate logging configuration in the " + \
            "following locations:")
        for location in conf_file_locations:
            print("   " + abspath(expanduser(location)))

