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

# Adjust path so we can see the src modules running from branch as well
# as test dir:
import sys
sys.path.insert(0, './src/')
sys.path.insert(0, '../src/')
sys.path.insert(0, '../../src/')
sys.path.insert(0, './test/')
sys.path.insert(0, './test/network/')
sys.path.insert(0, '../test/')
sys.path.insert(0, '../test/network/')

import unittest
from unittest import TestSuite

from twisted.internet import reactor
from twisted.spread import pb
import configureLogging
from logging import getLogger
logger = getLogger("rounder.networktests")

from rounder.network.server import SERVER_PORT
from rounder.network.client import NetworkClient

# The remote server object, assigned when the deferred callback is reached:
server = None

def launch_tests(root_object):
    ''' 
    Deferred callback that kicks off the tests once we have a referece to our
    remote object.
    '''
    global server 
    server = root_object

    # Kickoff the tests:
    try:
        import testoob
        testoob.main(defaultTest="suite")
    except ImportError:
        unittest.main(defaultTest="suite")

def error(reason):
    print "Error getting root object: ", reason

class ClientTests(unittest.TestCase):

    def setUp(self):
        self.client = NetworkClient(server)

    def test_login(self):
        deferred = self.client.login("joeblow", "encryptedpw")
        deferred.addCallback(self.assert_logged_in)

    def assert_logged_in(self, data):
        self.assertTrue(self.client.logged_in)



def suite():
    # Append all test suites here:
    return TestSuite((
        unittest.makeSuite(ClientTests),
    ))

if __name__ == '__main__':
    f = pb.PBClientFactory()
    reactor.connectTCP("localhost", SERVER_PORT, f)
    d = f.getRootObject()
    d.addCallbacks(launch_tests, error)
    reactor.run()

