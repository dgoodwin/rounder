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
from twisted.cred import checkers, portal, credentials, error
from twisted.internet import reactor, defer
from twisted.python import failure

from logging import getLogger
logger = getLogger("rounder.network.server")

from rounder.limit import FixedLimit
from rounder.table import Table
from rounder.currency import Currency
from rounder.dto import TableState, TableListing
from rounder.player import Player
from rounder.core import RounderException
from rounder.network.serialize import register_message_classes, dumps

DEFAULT_SERVER_PORT = 35100


class RounderNetworkServer(object):

    """
    Core Rounder Server

    Maintains the internal engine objects, as well as the lists of connected
    clients etc.

    Interface between the network layer and the underlying business objects.
    """

    def __init__(self):
        self.users = {} # hash of usernames to their perspectives
        self.table_views = {}

    def add_user(self, username, perspective):
        """
        Add a user perspective.

        Called when a user successfully authenticates and connects to the
        server.
        """
        logger.info("User connected to server: %s" % username)
        assert(not username in self.users.keys())
        self.users[username] = perspective

    def remove_user(self, username):
        """
        Remove a user perspective.

        Called when a user has disconnected.
        """
        logger.info("User disconnected from server: %s" % username)
        assert(username in self.users.keys())
        self.users.pop(username)

    def create_table(self, name):
        """ Create a new table. """
        # TODO: stop hard coding everything :)
        limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        table = Table(name=name, limit=limit, seats=10, server=self)

        view = TableView(table, self)
        self.table_views[table.id] = view
        return table

    def list_tables(self):
        """ Returns a list of visible tables to the client. """
        tables = []
        for t in self.table_views.values():
            tables.append(dumps(TableListing(t.table)))
        return tables

    def open_table(self, table_id, user):
        """
        Subscribe a user to a table.

        Returns a tuple of the user's newly created table view, and a
        TableState snapshot the client can use to draw the current table
        state.
        """
        logger.debug("Opening table %s for user %s" % (table_id,
                                                       user.username))
        # TODO: check if user should be allowed to observe this table.
        table = self.table_views[table_id].table
        table.add_observer(user.username)
        state = TableState(table)
        return (self.table_views[table_id], dumps(state))

    def seat_player(self, user, table, seat_num):
        """ Seat a player at a table in a specific seat. """
        player = Player(user.username, chips=Currency(1000))
        # TODO: error handling, what if seat already taken?
        try:
            table.seat_player(player, seat_num)
        except RounderException, e:
            raise e
        return seat_num

    def sit_out_player(self, table, user):
        """ Sit out a player. """
        player = table.seats.players_by_username[user.username]
        table.sit_out(player)

    def game_over(self, table):
        """ Called by a table whenever a game ends. """
        logger.debug("Table %s: game over")

    def prompt_player(self, table, username, actions):
        """ Called by a table to prompt a player with a list of actions. """
        log_msg = "Table %s: Prompting %s with actions:" % (table.id,
            username)
        serialized_actions = []
        for action in actions:
            log_msg += "\n  %s" % action
            serialized_actions.append(dumps(action))
        logger.debug(log_msg)
        self.users[username].prompt(table.id, serialized_actions)

    def notify(self, table_id, username, event):
        serialized_event = dumps(event)
        self.users[username].notify(table_id, serialized_event)

    def process_action(self, table, user, action_index, params):
        """ Process an incoming action from a player. """
        logger.debug("Table %s: Received action index %s from %s." %
            (table.id, action_index, user.username))
        table.process_action(user.username, action_index, params)


class RounderRealm(object):

    """ Creates perspectives/avatars. """

    def __init__(self):
        self.server = None

    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User(avatarId, self.server)
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a = avatar: a.detached(mind)


class User(pb.Avatar):

    """ An authenticated user's perspective. """

    def __init__(self, username, server):
        self.username = username
        self.server = server
        self.server.add_user(username, self)
        self.remote = None
        self.table_views = {}

    def attached(self, mind):
        self.remote = mind

    def detached(self, mind):
        self.remote = None
        self.server.remove_user(self.username)

        for tv in self.table_views.values():
            tv.table.remove_observer(self.username)

    def send(self, message):
        self.remote.callRemote("print", message)

    def perspective_list_tables(self):
        """ Lists available tables. """
        return self.server.list_tables()

    def perspective_open_table(self, table_id):
        """ Process a users request to view a table. """
        tuple = self.server.open_table(table_id, self)
        self.table_views[tuple[0].table.id] = tuple[0]
        return tuple

    def prompt(self, table_id, serialized_actions):
        """
        Prompt the player with a call to their remote perspective.

        Remote could be None in the case of testing, in which case we do
        nothing.
        """
        if self.remote != None:
            d = self.remote.callRemote("prompt", table_id, serialized_actions)
            d.addCallback(self.prompt_success_cb, self.prompt_failure_cb)

    def prompt_success_cb(self, data, failure_cb):
        """ Successful prompt callback. """
        pass

    def prompt_failure_cb(self, data):
        """ Failed prompt callback. """
        logger.debug("Prompt failed.")

    def notify(self, table_id, serialized_event):
        """
        Pass an Event along to the client.
        """
        if self.remote != None:
            d = self.remote.callRemote("notify", table_id, serialized_event)
            d.addCallback(self.notify_success_cb, self.notify_failure_cb)

    def notify_success_cb(self, data, failure_cb):
        """ Successful notify callback. """
        pass

    def notify_failure_cb(self, data):
        """ Failed notify callback. """
        logger.debug("Notify failed.")


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

    def view_sit_out(self, from_user):
        self.server.sit_out_player(self.table, from_user)

    def view_leave(self, from_user):
        """ Leave the table. """
        self.table.remove_observer(from_user.username)
        from_user.table_views.pop(self.table.id)

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

    def view_process_action(self, from_user, action_index, params):
        """
        Called by clients attempting to perform an action.
        """
        self.server.process_action(self.table, from_user, action_index,
                params)

    def view_chat_message(self, from_user, message):
        """
        Callled by clients to send a chat message to the table.
        """
        self.table.chat_message(from_user.username, message)


class OnDemandCredentialsChecker(object):
    """
    Our temporary credential checker.

    Checks if an incoming username exists in the in-memory hash and if so
    validate that it's password matches. If not, add the username and the
    current password. First come, first serve.

    Problems storing the md5 passwords we receive and using them to compare
    directly. All accounts are assumed to use "password" for now.
    """
    implements(checkers.ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword)

    def __init__(self):
        self.users = {}

    def addUser(self, username, password):
        logger.info("Creating user account: %s" % (username))
        self.users[username] = password

    def _cbPasswordMatch(self, matched, username):
        if matched:
            logger.info("User authenticated: %s" % username)
            return username
        else:
            logger.warn("Authentication failed for: %s" % username)
            return failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):

        if credentials.username not in self.users:
            self.addUser(credentials.username, "password")
        return defer.maybeDeferred(
            credentials.checkPassword,
            self.users[credentials.username]).addCallback(
            self._cbPasswordMatch, str(credentials.username))


def run_server():
    logger.info("Starting Rounder server on port %s" % (DEFAULT_SERVER_PORT))
    register_message_classes()

    realm = RounderRealm()
    realm.server = RounderNetworkServer()
    checker = OnDemandCredentialsChecker()
    p = portal.Portal(realm, [checker])

    realm.server.create_table("Table 1")

    reactor.listenTCP(DEFAULT_SERVER_PORT, pb.PBServerFactory(p))
    reactor.run()
