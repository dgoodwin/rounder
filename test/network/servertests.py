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
from rounder.action import Raise

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

        self.user1.table_views[self.table.id].view_start_game(self.user1)
        self.assertEquals(STATE_SMALL_BLIND, 
            self.table.gsm.get_current_state())

    def test_cannot_start_game_only_one_player(self):
        self.user1_table.view_start_game(self.user1)
        self.assertEquals(None, self.table.gsm.get_current_state())



class TestUser(User):

    def prompt(self, table_id, serialized_actions):
        """ 
        Override the parents prompt method to prompt a dummy client
        instead of a live one.
        """
        
        self.pending_actions = []
        for a in serialized_actions:
            action = loads(a)
            self.pending_actions.append(action)

    def act_randomly(self):
        if (len(self.pending_actions) == 0):
            raise Exception("No pending actions.")

        r = random.randint(0, len(self.pending_actions) - 1)
        random_action = self.pending_actions[r]
        params = []
        if isinstance(random_action, Raise):
            params.append(str(random_action.min_bet))
        self.server.process_action(self.table_views[table_id].table,
            self, r, params)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RounderNetworkServerTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
