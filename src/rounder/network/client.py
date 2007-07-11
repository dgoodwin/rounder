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
from twisted.internet import reactor, protocol

from logging import getLogger
logger = getLogger("rounder.network.client")

from rounder.network.protocol import LoginMessage

class NetworkClient(pb.Root):
    """
    Focal point for all client side network communication.

    All local requests pass through here en route to the server, likewise
    for all incoming data from the server.

    Maintains a reference to the remote server object.

    Maintains a reference to the local client side user interface, which
    is notified on all incoming requests/responses.
    """

    def __init__(self, server):
        self.server = server
        # TODO: pass ref to self back to the server

        self.logged_in = False

    def login(self, username, password):
        deferred = self.server.callRemote("login", "joeblow", "encryptedpw")
        deferred.addCallbacks(self.login_success_cb, self.login_failure_cb)
        return deferred

    def login_success_cb(self, data):
        logger.debug("Logged in: " + data)
        self.logged_in = True

    def login_failure_cb(self, data):
        logger.debug("Login failed: " + data)


