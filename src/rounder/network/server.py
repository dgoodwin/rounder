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

from zope.interface import implements
from twisted.spread import pb
from twisted.cred import checkers, portal
from twisted.internet import reactor

from logging import getLogger
logger = getLogger("rounder.network.server")

from rounder.limit import FixedLimit
from rounder.table import Table
from rounder.currency import Currency
from rounder.dto import TableState
from rounder.player import Player
from rounder.core import RounderException
from rounder.network.serialize import register_message_classes, dumps

SERVER_PORT = 35100

class RounderNetworkServer:

    """ 
    Core Rounder Server 
    
    Maintains the internal engine objects, as well as the lists of connected
    clients etc.

    Interface between the network layer and the underlying business objects.
    """

    def __init__(self):
        self.users = {} # hash of usernames to their perspectives
        self.table_views = {}

    def create_table(self, name):
        """ Create a new table. """
        # TODO: stop hard coding everything :)
        limit = FixedLimit(small_bet=Currency(1), big_bet=Currency(2))
        table = Table(name=name, limit=limit, seats=10)

        view = TableView(table, self)
        self.table_views[table.id] = view
        return table

    def list_tables(self):
        """ Returns a list of visible tables to the client. """
        tables = []
        for t in self.table_views.values():
            tables.append((t.table.id, t.table.name))
        return tables

    def open_table(self, table_id, user):
        """ 
        Subscribe a user to a table. 

        Returns a tuple of the user's newly created table view, and a 
        TableState snapshot the client can use to draw the current table
        state.
        """
        logger.debug("Opening table %s for user %s" % (table_id, user.name))
        # TODO: check if user should be allowed to observe this table.
        table = self.table_views[table_id].table
        table.observers.append(user)
        state = TableState(table)
        return (self.table_views[table_id], dumps(state))

    def seat_player(self, user, table, seat_num):
        """ Seat a player at a table in a specific seat. """
        player = Player(user.name, chips=Currency(1000))
        # TODO: error handling, what if seat already taken?
        table.seat_player(player, seat_num)
        return (table.id, seat_num)



class RounderRealm:

    """ Creates perspectives/avatars. """

    def __init__(self):
        self.server = None

    implements(portal.IRealm) 
    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User(avatarId, self.server)
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a = avatar : a.detached(mind)



class User(pb.Avatar):

    """ An authenticated user's perspective. """

    def __init__(self, name, server):

        logger.info("User authenticated: %s" % name)
        self.name = name
        self.server = server
        self.server.users[self.name] = self
        self.remote = None

    def attached(self, mind):
        self.remote = mind

    def detached(self, mind):
        self.remote = None

    def send(self, message):
        self.remote.callRemote("print", message)

    def perspective_list_tables(self):
        """ Lists available tables. """
        return self.server.list_tables()

    def perspective_open_table(self, table_id):
        """ Process a users request to view a table. """
        return self.server.open_table(table_id, self)



class TableView(pb.Viewable):

    """ 
    User's perspective of a table. Created at the same time a 
    rounder.table.Table would be.

    One created per table, not per user.

    Protects from spoofing by inserting a reference to the users avatar
    automatically into the arguments of all remote calls.

    Remote methods prefixed with view_ here.
    """

    def __init__(self, table, server):
        self.table = table
        self.server = server

    def view_sit(self, from_user, seat):
        return self.server.seat_player(from_user, self.table, seat)

    def view_start_game(self, from_user):
        """ 
        Called when a user requests a new hand be started.

        Verifies that when this request is received, a hand is not already
        underway, and that we have enough players, before anything
        actually happens.
        """
        try:
            self.table.begin()
        except RounderException:
            logger.warn("Error starting game at table. Not enough players?")
         


def run_server():
    logger.info("Starting Rounder server on port %s" % (SERVER_PORT))
    register_message_classes()
    
    realm = RounderRealm()
    realm.server = RounderNetworkServer()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser("joe", "password")
    p = portal.Portal(realm, [checker])

    realm.server.create_table("Table 1")

    reactor.listenTCP(SERVER_PORT, pb.PBServerFactory(p))
    reactor.run()

