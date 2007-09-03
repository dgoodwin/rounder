
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
from server.servertests import BaseServerFixture

class EventTests(BaseServerFixture):

    def setUp(self):
        BaseServerFixture.setUp(self)

    def test_player_joined_events(self):
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(0, len(self.user2.events))
        self.user1_table.view_sit(self.user1, 0)
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
