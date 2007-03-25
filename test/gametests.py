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

""" Tests for the rounder.game module. """

import unittest

import settestpath

from rounder.player import Player
from rounder.limit import FixedLimit
from rounder.game import TexasHoldemGame

class TexasHoldemTests(unittest.TestCase):

    def test_walkthrough(self):
        p1 = Player('Player 1', 1000)
        p2 = Player('Player 2', 1000)
        p3 = Player('Player 3', 1000)
        limit = FixedLimit(small_bet=2, big_bet=4)
        players = [p1, p2, p3]
        game = TexasHoldemGame(limit=limit, players=players, dealer=0)
        game.start()



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TexasHoldemTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
