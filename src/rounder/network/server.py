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

""" The Rounder Server Module """

import simplejson
from twisted.internet import reactor, protocol

from logging import getLogger
logger = getLogger("rounder.network.server")

SERVER_PORT = 35100

class RounderProtocol(protocol.Protocol):

    def connectionMade(self):
        logger.debug("client connected")

    def dataReceived(self, data):
        logger.debug("data received: %s", data)
        obj = simplejson.loads(data)
        logger.debug("   obj type = %s", type(obj))
        logger.debug("   obj = %s", str(obj))



def run_server():
    logger.info("Starting Rounder server on port %s" % (SERVER_PORT))
    factory = protocol.ServerFactory()
    factory.protocol = RounderProtocol
    reactor.listenTCP(SERVER_PORT, factory)
    reactor.run()

