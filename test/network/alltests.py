#!/usr/bin/env python

#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

import unittest

from unittest import TestSuite

from twisted.internet import reactor

# Adjust path so we can see the src modules running from branch as well
# as test dir:
sys.path.insert(0, './src/')
sys.path.insert(0, '../src/')
sys.path.insert(0, '../../src/')
sys.path.insert(0, '../../../src/')
sys.path.insert(0, './test/')

import configureLogging

# Import all test modules here:
import clienttests

from rounder.network.client import RounderClientFactory
from rounder.network.server import SERVER_PORT

f = RounderClientFactory()
reactor.connectTCP("localhost", SERVER_PORT, f)
reactor.run()

def suite():
    # Append all test suites here:
    return TestSuite((
        clienttests.suite(),
    ))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
