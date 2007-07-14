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

import cerealizer

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials

from logging import getLogger
logger = getLogger("rounder.network.client")

class RounderNetworkClient(pb.Referenceable):

    """
    Focal point for all client side network communication.

    All local requests pass through here en route to the server, likewise
    for all incoming data from the server.

    Maintains a reference to the remote server object.

    Maintains a reference to the local client side user interface, which
    is notified on all incoming requests/responses.
    """

    def remote_print(self, message):
        print message

    def connect(self, host, port, user, password):
        factory = pb.PBClientFactory()
        reactor.connectTCP(host, port, factory)
        def1 = factory.login(credentials.UsernamePassword(user, password),
            client=self)
        def1.addCallback(self.connected)
        reactor.run()

    def connected(self, perspective):
        logger.debug("connected!")
        logger.debug("perspective = %s" % perspective)
        # this perspective is a reference to our User object
#d = perspective.callRemote("joinGroup", "#lookingForFourth")
#        d.addCallback(self.gotGroup)

#def gotGroup(self, group):
#    print "joined group, now sending a message to all members"
#    # 'group' is a reference to the Group object (through a ViewPoint)
#    d = group.callRemote("send", "You can call me Al.")
#    d.addCallback(self.shutdown)

    def shutdown(self, result):
        reactor.stop()


