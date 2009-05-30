#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#   Copyright (C) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
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

""" Tests for the rounder.player module. """

import unittest

from rounder.player import Player
from rounder.core import InvalidPlay
from rounder.currency import Currency
from utils import create_players


class PlayerTests(unittest.TestCase):

    def setUp(self):
        self.player = create_players([100])[0]

    def test_bet_zero(self):
        """ Bet zero  on a second+ round of betting. """
        self.assertRaises(InvalidPlay, self.player.bet, 0, 1)
        self.assertRaises(InvalidPlay, self.player.bet, 0, 2)
        self.assertRaises(InvalidPlay, self.player.bet, 0, 100)

    def test_bet_toomuch(self):
        self.assertRaises(InvalidPlay, self.player.bet, 101, 0)

    def test_bet_normal(self):
        self.player.bet(10, 0)

    def test_take_bet(self):
        self.player.bet(10, 0)
        self.assertEquals(10, self.player.new_round(),
            "Player didn't seem to bet")

    def test_take_second_round_bet(self):
        self.player.bet(10, 0)
        self.player.new_round()
        self.player.bet(5, 1)
        self.assertEquals(5, self.player.new_round(),
            "Player bet is incorrect")

    def test_something(self):
        pass

