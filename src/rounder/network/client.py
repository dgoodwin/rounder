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

""" The Rounder Client Module """

import simplejson
from twisted.internet import reactor, protocol

from logging import getLogger
logger = getLogger("rounder.network.client")

class RounderClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(simplejson.dumps("hello, world!"))

    def dataReceived(self, data):
        logger.debug("data received: %s", data)
        obj = simplejson.loads(data)
        logger.debug("   obj type = %s", type(obj))
        logger.debug("   obj = %s", str(obj))
#self.transport.loseConnection()

#    def connectionLost(self, reason):
#        print "connection lost"

class RounderClientFactory(protocol.ClientFactory):
    protocol = RounderClient

    def startedConnecting(self, connector):
        logger.debug("Connecting to server.")

    def buildProtocol(self, addr):
        logger.debug("Connected!")
        return RounderClient()

    def clientConnectionFailed(self, connector, reason):
        logger.debug("Connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        # TODO: reconnect?
        logger.debug("Connection lost.")
        reactor.stop()


