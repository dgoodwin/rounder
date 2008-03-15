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
        self.tables = {} # Hash of table id's to ClientTable objects
        self.username = None
        self.host = None
        self.port = None

    def connect(self, host, port, username, password):
        """ Initiate connection to a server. """
        factory = pb.PBClientFactory()
        self.host = host
        self.port = port
        self.username = username
        reactor.connectTCP(host, port, factory)
        def1 = factory.login(credentials.UsernamePassword(username, password),
            client=self)
        def1.addCallbacks(self.connect_success_cb, self.connect_failure_cb)
        def1.addErrback(self.log_error)
        reactor.run()

    @staticmethod
    def shutdown():
        reactor.stop()

    def log_error(self, failure):
        self.ui.log_error(failure)

    def connect_success_cb(self, perspective):
        """ Callback for successful connection. """
        logger.debug("connected!")
        self.perspective = perspective
        self.ui.connect_success(self)

    def connect_failure_cb(self, failure):
        """ Callback for a failed connection attempt. """
        logger.debug("Connection failed: %s" % failure)
        self.ui.connect_failure()

    def get_table_list(self):
        """ Request a list of tables from the server. """
        logger.debug("requesting table list")
        d = self.perspective.callRemote("list_tables")
        d.addCallbacks(self.get_table_list_success_cb, 
            self.get_table_list_failure_cb)
        d.addErrback(self.log_error)

    def get_table_list_success_cb(self, data):
        """ Called when a list of tables is received. """
        logger.debug("got table list")
        table_listings = []
        for t in data:
            temp = loads(t)
            logger.debug("   %s" % temp)
            table_listings.append(temp)
        self.ui.got_table_list(table_listings)

    def get_table_list_failure_cb(self, failure):
        """ Callback for a failed get tables attempt. """
        pass

    def open_table(self, table_id):
        """ Open a table. """
        logger.debug("Opening table: %s" % table_id)
        d = self.perspective.callRemote("open_table", table_id)
        d.addCallbacks(self.open_table_success_cb, self.log_error)

    def open_table_success_cb(self, data):
        """ Callback for a successful table open. """
        table_view = data[0]
        table_state = loads(data[1])
        logger.debug("Table opened successfully: %s" % table_state.name)

        table = ClientTable(table_view, table_state)
        self.tables[table_state.id] = table
        self.ui.open_table_success_cb(table)

    def remote_prompt(self, table_id, actions):
        """
        Prompt player to choose one of the given actions for a table.
        """
        # TODO: I don't yet see a way to get the server a reference to the 
        # ClientTables, but I'm sure there's a way. Until this is adressed,
        # will delegate the call there manually:
        self.tables[table_id].prompt(actions)

    def remote_notify(self, table_id, event):
        """
        Display an incoming event to the user.
        """
        deserialized_event = loads(event)
        logger.debug("Table %s: received event: %s" % (table_id,
            deserialized_event))
        # TODO
        self.tables[table_id].process_event(deserialized_event)

    def remote_print(self, msg):
        logger.warn("Server said: %s" % msg)



class ClientTable(pb.Referenceable):
    """
    A client side table object maintaining state of the table and exposing
    remote methods the UI can call to interact with the table on the server.

    Thin wrapper over the Rounder server's TableView object.
    """

    def __init__(self, table_view, table_state):
        """
        Initialize the table with the given remote view and state received 
        from the server.
        """
        self.__view = table_view
        self.state = table_state
        self.ui = None

    def log_error(self, failure):
        self.ui.log_error(failure)

    def sit(self, seat):
        """ Request the specified seat index at the specified table. """
        logger.debug("Requesting seat %s at table %s" % (seat, 
            self.state.id))
        d = self.__view.callRemote("sit", seat)
        d.addCallback(self.sit_success_cb)
        d.addErrback(self.log_error)

    def sit_success_cb(self, data):
        """ Callback for successfully taking a seat at the table. """
        seat_num = data
        logger.debug("Succesfully took seat %s at table: %s" % (seat_num,
            self.state.id))
        self.ui.sit_success(seat_num)

    def start_game(self):
        """ Request the server start a new game at this table. """
        d = self.__view.callRemote("start_game")

    def leave(self):
        """ Leave this table. """
        logger.info("Table %s: Leaving." % self.state.id)
        d = self.__view.callRemote("leave")

    def prompt(self, serialized_actions):
        """ 
        Deserialize the given actions and prompt the ui to choose one. 
        """
        logger.debug("Table %s: received actions:" % self.state.id)
        try:
            deserialized_actions = []
            for action in serialized_actions:
                action = loads(action)
                logger.debug("   %s" % action)
                deserialized_actions.append(action)

            # TODO: save actions provided for client side validation

            self.ui.prompt(deserialized_actions)
        except Exception, e:
            logger.error(e)
            raise e

    def act(self, table_id, action_index, params):
        """
        Server prompts clients with a list of actions. To ensure the client
        never carries out an action it wasn't given the option to, actions are
        selected by an index into the list the server sent.
        """
        # TODO: add parameters here
        logger.debug("Table %s: Sending action index %s to server: %s" %
            (table_id, action_index, params))
        self.view.callRemote("process_action", action_index,
            params)

    def process_event(self, event):
        """
        Called by the parent network client when it receives and event we
        need to display to the user for this table.
        """
        self.state = event.table_state
        self.ui.process_event(event)


