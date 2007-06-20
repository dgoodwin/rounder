#!/usr/bin/env python
"""
Thin script to run rounder from the source directory. (and not the installed
version.
"""

import sys
sys.path.insert(0, './src/')

from rounder.log import setup_logging
# Configure logging: (needs to be done before importing our modules)
confFileLocations = ["~/.rounder/logging.conf", "./logging.conf"]
setup_logging(confFileLocations)

from rounder.core import RounderApplication

if __name__ == "__main__":
    rounderApp = RounderApplication()
    rounderApp.main()

