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
from rounder.pot import Pot
from utils import create_players_list

CHIPS = 1000

class SidePotTests(unittest.TestCase):

    def test_side_pot_created_all_in_raise(self):
        self.players = create_players_list(4, CHIPS)
        self.players[0].chips = Currency(400)
        self.players[1].chips = Currency(500)
        pot = Pot(self.players)
        self.assertEquals(1, len(pot.pots))

        pot.add(self.players[0], Currency(400))
        pot.add(self.players[1], Currency(500))
        self.assertEquals(2, len(pot.pots))

    def test_side_pot_created_all_in_call(self):
        pass



class SplitPotTests(unittest.TestCase):

    def test_simple_case(self):
        self.players = create_players_list(4, 0)
        self.pot = Pot(players=self.players)
        self.pot.pots[0].amount = Currency(10)
        self.pot.split([self.players[0]])
        self.assertEquals(10, self.players[0].chips)

    def test_even_split_case(self):
        self.players = create_players_list(4, 0)
        self.pot = Pot(players=self.players)
        self.pot.pots[0].amount = Currency(10)
        self.pot.split(self.players[0:2])
        self.assertEquals(5, self.players[0].chips)
        self.assertEquals(5, self.players[1].chips)

    def test_uneven_split_case(self):
        self.players = create_players_list(4, 0)
        self.pot = Pot(players=self.players)
        self.pot.pots[0].amount = Currency(0.25)
        self.pot.split(self.players[0:2])
        self.assertEquals(0.13, self.players[0].chips)
        self.assertEquals(0.12, self.players[1].chips)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SidePotTests))
    suite.addTest(unittest.makeSuite(SplitPotTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
