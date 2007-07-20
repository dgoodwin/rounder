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

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials

from logging import getLogger
logger = getLogger("rounder.network.client")

from rounder.network.serialize import loads

class RounderNetworkClient(pb.Referenceable):

    """
    Focal point for all client side network communication.

    All local requests pass through here en route to the server, likewise
    for all incoming data from the server.

    Maintains a reference to the remote server object.

    Maintains a reference to the local client side user interface, which
    is notified on all incoming requests/responses.

    Responsible for ANY de-serialization or parsing of tuples returned from
    the server. Calls to the UI should be clean, readable, and use objects
    whenever possible.

    Callback methods for a method X should be named X_success_cb and 
    X_success_failure_cb.
    """

    def __init__(self, ui):
        """ 
        Initializes a network client.

            ui = Reference to a client user interface where we can pass
                responses on to.
        """
        self.ui = ui
        self.table_views = {}

    def connect(self, host, port, user, password):
        """ Initiate connection to a server. """
        factory = pb.PBClientFactory()
        reactor.connectTCP(host, port, factory)
        def1 = factory.login(credentials.UsernamePassword(user, password),
            client=self)
        def1.addCallback(self.connected)
        reactor.run()

    @staticmethod
    def shutdown():
        reactor.stop()

    def connected(self, perspective):
        """ Callback for successful connection. """
        logger.debug("connected!")
        self.perspective = perspective
        self.ui.connected()

    def get_table_list(self):
        """ Request a list of tables from the server. """
        logger.debug("requesting table list")
        d = self.perspective.callRemote("list_tables")
        d.addCallback(self.get_table_list_success_cb)

    @staticmethod
    def get_table_list_success_cb(data):
        """ Called when a list of tables is received. """
        logger.debug("got table list")
        self.ui.got_table_list(data)

    def open_table(self, table_id):
        """ Open a table. """
        logger.debug("Opening table: %s" % table_id)
        d = self.perspective.callRemote("open_table", table_id)
        d.addCallback(self.open_table_success_cb)

    def open_table_success_cb(self, data):
        """ Callback for a successful table open. """
        table_view = data[0]
        table_state = loads(data[1])
        logger.debug("Table opened successfully: %s" % table_state.name)
        self.table_views[table_state.id] = table_view
        self.ui.table_opened(table_state)

    def take_seat(self, table_id, seat):
        """ Request the specified seat index at the specified table. """
        d = self.table_views[table_id].callRemote("sit", seat)
        d.addCallback(self.take_seat_success_cb)

    def take_seat_success_cb(self, data):
        """ Callback for successfully sitting down. """
        table_id = data[0]
        seat_num = data[1]
        logger.debug("Succesfully took seat %s at table: %s" % (seat_num,
            table_id))
        self.ui.took_seat(table_id, seat_num)

    def start_game(self, table_id):
        """ Request the server start a new game at a table. """
        d = self.table_views[table_id].callRemote("start_game")
