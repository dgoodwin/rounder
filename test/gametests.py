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
from rounder.currency import Currency

CHIPS = 1000

class TexasHoldemTests(unittest.TestCase):

    def __create_game(self, numPlayers, dealerIndex):
        self.players = []
        for i in range(numPlayers):
            self.players.append(Player('player' + str(i), Currency(CHIPS)))
        limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        self.game = TexasHoldemGame(limit=limit, players=self.players, 
            dealer=dealerIndex)

    def test_standard_post_blinds(self):
        self.__create_game(3, 0)
        self.game.post_blinds()
        # TODO: check blinds were gathered
        self.assertEquals(CHIPS - 1, self.players[1].chips)
        self.assertEquals(CHIPS - 2, self.players[2].chips)
        self.assertEquals(CHIPS, self.players[0].chips)


    def test_walkthrough(self):
        pass

    # test_insufficient_funds_for_blinds
    # test_blind_rejected
    # test_blinds_wraparound



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TexasHoldemTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
