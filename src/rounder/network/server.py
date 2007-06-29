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

from twisted.spread import pb
from twisted.internet import reactor, protocol

from logging import getLogger
logger = getLogger("rounder.network.server")

#from rounder.network.protocol import register_message_classes

SERVER_PORT = 35100

#class RounderProtocol(protocol.Protocol):

#    def connectionMade(self):
#        logger.debug("client connected")

#    def dataReceived(self, data):
#        obj = cerealizer.loads(data)
#        logger.debug("received: %s", str(obj))

class ServerController(pb.Root):
    """
    Core server controller, remotely referencable and the focal point for
    all client requests.
    """

    def remote_login(self, login, password_hash):
        """ Process a login request. """
        logger.debug("Successful login: %s" % login)


def run_server():
    logger.info("Starting Rounder server on port %s" % (SERVER_PORT))
#    register_message_classes()
#    factory = protocol.ServerFactory()
#    factory.protocol = RounderProtocol
    reactor.listenTCP(SERVER_PORT, pb.PBServerFactory(ServerController()))
    reactor.run()

