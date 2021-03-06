#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
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

import unittest
import random

from rounder.network.server import RounderNetworkServer, User
from rounder.network.serialize import loads
from rounder.action import Raise, Call, Fold

__all__ = []

class BaseServerFixture(unittest.TestCase):

    """ Base class for tests that require a server object. """

    def setUp(self):
        self.server = RounderNetworkServer()
        self.table_name = "Test Table 1"
        self.table = self.server.create_table(self.table_name)

        self.user1 = TestUser("Test Player 1", self.server)
        self.user2 = TestUser("Test Player 2", self.server)
        self.user1.perspective_open_table(self.table.id)
        self.user2.perspective_open_table(self.table.id)
        self.user1_table = self.user1.table_views[self.table.id]
        self.user2_table = self.user1.table_views[self.table.id]

        self.users = [self.user1, self.user2]

    def clear_player_events(self):
        """
        Clears the stored events for each player. Used in a test
        immediately before doing something we expect to trigger events.
        """
        for user in self.users:
            user.events = []


class TestUser(User):

    def __init__(self, username, server):
        User.__init__(self, username, server)

        # Queue of all events received.
        self.events = []

    def prompt(self, table_id, serialized_actions):

        # TODO: refactor to list of pending actions per table
        self.pending_actions = []
        for a in serialized_actions:
            action = loads(a)
            self.pending_actions.append(action)

    def act_randomly(self, table_id):
        """
        Choose a random action from the pending list.
        """
        if (len(self.pending_actions) == 0):
            raise Exception("No pending actions.")

        r = random.randint(0, len(self.pending_actions) - 1)
        random_action = self.pending_actions[r]
        params = []
        if isinstance(random_action, Raise):
            params.append(str(random_action.min_bet))
        self.pending_actions = []
        self.server.process_action(self.table_views[table_id].table,
            self, r, params)

    def act(self, table_id, action_type, params=None):
        i = 0
        if params is None:
            params = []
        for action in self.pending_actions:
            if isinstance(action, action_type):
                self.pending_actions = []
                self.server.process_action(self.table_views[table_id].table,
                    self, i, params)
            i += 1

        raise Exception("Unable to find action of type %s" % action_type)

    def notify(self, table_id, serialized_event):
        """
        Override the parent to track events sent.
        """
        User.notify(self, table_id, serialized_event)
        self.events.append(loads(serialized_event))

    def act(self, table_id, action_type, param=None):
        """
        Locate an action of the specified type in the pending list and submit
        to the server, with an optional parameter.
        """
        if (len(self.pending_actions) == 0):
            raise Exception("No pending actions.")

        found = False
        i = 0
        for a in self.pending_actions:
            if isinstance(a, action_type):
                self.pending_actions = []
                self.server.process_action(self.table_views[table_id].table,
                        self, i, param)
                return
            else:
                i = i + 1
        if not found:
            raise Exception("Unable to locate action of type: %s", action_type)


