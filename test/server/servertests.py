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

""" Tests for the rounder.network.server module. """

from logging import getLogger
logger = getLogger("rounder.test.network.servertests")

import unittest
import random

import settestpath

from rounder.network.server import RounderNetworkServer, User, TableView
from rounder.table import STATE_SMALL_BLIND
from rounder.network.serialize import loads
from rounder.action import Raise, Call, Fold

class RounderNetworkServerTests(unittest.TestCase):

    """ Tests exercising the server network controller. """

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

    def find_user_with_pending_actions(self):
        for u in self.users:
            if len(u.pending_actions) > 0:
                return u
        raise Exception("Unable to find a player with pending actions.")

    def test_open_table(self):
        self.assertTrue(isinstance(self.user1.table_views[self.table.id], 
            TableView))

    def test_list_tables(self):
        table_list = self.server.list_tables()

    def test_seat_player(self):
        self.server.seat_player(self.user1, self.table, 0)

    def test_start_game(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)

        self.user1_table.view_start_game(self.user1)
        self.assertEquals(STATE_SMALL_BLIND, 
            self.table.gsm.get_current_state())

    def test_cannot_start_game_only_one_player(self):
        self.user1_table.view_start_game(self.user1)
        self.assertEquals(None, self.table.gsm.get_current_state())

    def test_full_hand(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)

        self.user1_table.view_start_game(self.user1)

        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)

        while self.table.game_underway():
            user = self.find_user_with_pending_actions()
            user.act_randomly(self.table.id)

    def test_player_joined_events_are_sent(self):
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(0, len(self.user2.events))
        self.user1_table.view_sit(self.user1, 0)
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))



class TestUser(User):

    def __init__(self, name, server):
        User.__init__(self, name, server)

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



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RounderNetworkServerTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
