#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2007 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006-2007 James Bowes <jbowes@dangerouslyinc.com>
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

""" Tests for the Rounder pot module. """

from logging import getLogger
logger = getLogger("rounder.test.gametests")

import unittest

import settestpath

from rounder.currency import Currency
from rounder.pot import PotManager
from rounder.core import RounderException
from utils import create_players_list, create_players

CHIPS = 1000

class PotTests(unittest.TestCase):

    def test_add_to_much(self):
        self.players = create_players([400, 500, 500, 700])
        pot_mgr = PotManager(self.players)
        self.assertRaises(AssertionError, pot_mgr.add,
            self.players[0], Currency(401))


    def test_side_pot_created_all_in_raise(self):
        self.players = create_players_list(4, CHIPS)
        self.players[0].chips = Currency(400)
        self.players[1].chips = Currency(500)
        pot_mgr = PotManager(self.players)
        self.assertEquals(1, len(pot_mgr.pots))

        pot_mgr.add(self.players[0], Currency(400))
        pot_mgr.add(self.players[1], Currency(500))
        self.assertEquals(2, len(pot_mgr.pots))

        self.assertEquals(400, pot_mgr.pots[0].bet_to_match)
        self.assertEquals(800, pot_mgr.pots[0].amount)
        self.assertEquals(4, len(pot_mgr.pots[0].players))

        self.assertEquals(100, pot_mgr.pots[1].bet_to_match)
        self.assertEquals(100, pot_mgr.pots[1].amount)
        self.assertEquals(3, len(pot_mgr.pots[1].players))

    def test_third_side_pot_created(self):
        self.players = create_players([400, 500, 500, 700])
        pot_mgr = PotManager(self.players)
        self.assertEquals(1, len(pot_mgr.pots))

        pot_mgr.add(self.players[0], Currency(400))
        pot_mgr.add(self.players[1], Currency(500))
        self.assertEquals(2, len(pot_mgr.pots))

        # Check the first pot:
        self.assertEquals(400, pot_mgr.pots[0].bet_to_match)
        self.assertEquals(800, pot_mgr.pots[0].amount)
        self.assertEquals(4, len(pot_mgr.pots[0].players))

        # Check the second pot:
        self.assertEquals(100, pot_mgr.pots[1].bet_to_match)
        self.assertEquals(100, pot_mgr.pots[1].amount)
        self.assertEquals(3, len(pot_mgr.pots[1].players))

    def test_side_pot_created_all_in_call(self):
        self.players = create_players([500, 300, 500])
        pot_mgr = PotManager(self.players)
        self.assertEquals(1, len(pot_mgr.pots))

        pot_mgr.add(self.players[0], Currency(400))
        pot_mgr.add(self.players[1], Currency(300))
        self.assertEquals(2, len(pot_mgr.pots))

        self.assertEquals(300, pot_mgr.pots[0].bet_to_match)
        self.assertEquals(600, pot_mgr.pots[0].amount)
        self.assertEquals(3, len(pot_mgr.pots[0].players))
        self.assertTrue(self.players[1] in pot_mgr.pots[0].players)

        self.assertEquals(100, pot_mgr.pots[1].bet_to_match)
        self.assertEquals(100, pot_mgr.pots[1].amount)
        self.assertEquals(2, len(pot_mgr.pots[1].players))
        self.assertFalse(self.players[1] in pot_mgr.pots[1].players)

    def assert_pots(self, pot_mgr, expected):
        self.assertEquals(len(expected), len(pot_mgr.pots))
        for i in range(len(expected)):
            self.assertEquals(expected[i], pot_mgr.pots[i].amount)

    def test_nightmare_scenario(self):
        self.players = create_players([1000, 300, 1000, 500, 100, 1000])
        pot_mgr = PotManager(self.players)
        
        pot_mgr.add(self.players[0], Currency(400))
        pot_mgr.add(self.players[1], Currency(300))
        self.assert_pots(pot_mgr, [600, 100])

        pot_mgr.add(self.players[2], Currency(400))
        self.assert_pots(pot_mgr, [900, 200])

        pot_mgr.add(self.players[3], Currency(500))
        self.assert_pots(pot_mgr, [1200, 400])

        pot_mgr.add(self.players[4], Currency(100))
        self.assert_pots(pot_mgr, [500, 800, 400])

        pot_mgr.add(self.players[5], Currency(500))
        self.assert_pots(pot_mgr, [600, 1000, 600])

        pot_mgr.add(self.players[0], Currency(100))
        self.assert_pots(pot_mgr, [600, 1000, 700])

        pot_mgr.add(self.players[2], Currency(100))
        self.assert_pots(pot_mgr, [600, 1000, 800])



class SplitPotTests(unittest.TestCase):

    def test_simple_case(self):
        self.players = create_players_list(4, 0)
        self.pot = PotManager(players=self.players)
        self.pot.pots[0].amount = Currency(10)
        self.pot.split([self.players[0]])
        self.assertEquals(10, self.players[0].chips)

    def test_even_split_case(self):
        self.players = create_players_list(4, 0)
        self.pot = PotManager(players=self.players)
        self.pot.pots[0].amount = Currency(10)
        self.pot.split(self.players[0:2])
        self.assertEquals(5, self.players[0].chips)
        self.assertEquals(5, self.players[1].chips)

    def test_uneven_split_case(self):
        self.players = create_players_list(4, 0)
        self.pot = PotManager(players=self.players)
        self.pot.pots[0].amount = Currency(0.25)
        self.pot.split(self.players[0:2])
        self.assertEquals(0.13, self.players[0].chips)
        self.assertEquals(0.12, self.players[1].chips)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PotTests))
    suite.addTest(unittest.makeSuite(SplitPotTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
