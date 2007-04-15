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

""" Tests for the rounder.table module. """

import unittest

import settestpath

from rounder.table import Table, Seats
from rounder.player import Player
from rounder.core import RounderException
from rounder.currency import Currency
from rounder.table import STATE_SMALL_BLIND, STATE_BIG_BLIND
from rounder.limit import FixedLimit
from rounder.action import SitOut, PostBlind

from utils import find_action_in_list

CHIPS = 1000

class SeatsTests(unittest.TestCase):

    def test_create_seats(self):
        seats = Seats(10)
        self.assertEqual(10, seats.get_size())

    def test_take_seat(self):
        seats = Seats(10)
        p = Player("Some Player")
        seats.seat_player(p, 0)
        self.assertEquals(p, seats.get_player(0))

    def test_zero_seat(self):
        seats = Seats(10)
        p = Player("Some Player")
        self.assertRaises(RounderException, seats.seat_player, p, -1)

    def test_too_high_seat(self):
        seats = Seats(10)
        p = Player("Some Player")
        self.assertRaises(RounderException, seats.seat_player, p, 10)

    def test_occupied_seat(self):
        seats = Seats(10)
        p = Player("Some Player")
        p2 = Player("Another Player")
        seats.seat_player(p, 0)
        self.assertRaises(RounderException, seats.seat_player, p2, 0)



class TableTests(unittest.TestCase):

    def __create_game(self, num_players, dealer_index):
        self.limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        self.table = Table(name="Test Table", limit=self.limit, seats=10)

        self.players = []
        for i in range(num_players):
            new_player = Player('player' + str(i), Currency(CHIPS))
            self.table.seat_player(new_player, i)
            self.players.append(new_player)

    # def test_not_enough_players_to_start_game

    def test_standard_post_blinds(self):
        self.__create_game(3, 0)
        self.table.start_hand()
        self.assertEquals(STATE_SMALL_BLIND, self.table.gsm.get_current_state())
        sb = self.players[1]
        self.assertEquals(2, len(sb.pending_actions))
        self.assertEquals(None, self.table.small_blind)

        # simulate player posting small blind:
        post_sb_action = find_action_in_list(PostBlind, sb.pending_actions)
        self.table.process_action(post_sb_action)
        self.assertEquals(STATE_BIG_BLIND, self.table.gsm.get_current_state())
        self.assertEquals(sb, self.table.small_blind)
        bb = self.players[2]
        self.assertEquals(2, len(bb.pending_actions))

        # simulate player posting big blind:
        post_bb_action = find_action_in_list(PostBlind, bb.pending_actions)
        self.assertEquals(None, self.table.big_blind)
        self.table.process_action(post_bb_action)
        self.assertEquals(bb, self.table.big_blind)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TableTests))
    suite.addTest(unittest.makeSuite(SeatsTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
