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

from rounder.network.server import RounderNetworkServer, User, TableView
from rounder.dto import TableState

class RounderNetworkServerTests(unittest.TestCase):

    """ Tests exercising the server network controller. """

    def setUp(self):
        self.server = RounderNetworkServer()
        self.table_name = "Test Table 1"
        self.table = self.server.create_table(self.table_name)
        self.table_id = self.table.id

        self.user = User("Test Player 1", self.server)

    def test_open_table(self):
        tuple = self.server.open_table(self.table_id, self.user)
        self.assertTrue(isinstance(tuple[0], TableView))

    def test_list_tables(self):
        table_list = self.server.list_tables()

    def test_seat_player(self):
        self.server.seat_player(self.user, self.table, 0)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RounderNetworkServerTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
