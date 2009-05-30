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

import settestpath

from rounder.network.server import TableView
from rounder.table import STATE_SMALL_BLIND

from rounder.network.serialize import register_message_classes
register_message_classes()

from server import BaseServerFixture

class RounderNetworkServerTests(BaseServerFixture):

    """ Tests exercising the server network controller. """

    def setUp(self):
        BaseServerFixture.setUp(self)

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

        while self.table.hand_underway():
            user = self.find_user_with_pending_actions()
            user.act_randomly(self.table.id)

    def test_remove_user(self):
        self.assertTrue(self.user1.username in self.server.users.keys())
        self.user1.detached(None)
        self.assertFalse(self.user1.username in self.server.users.keys())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RounderNetworkServerTests))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
