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
from rounder.table import STATE_SMALL_BLIND, STATE_BIG_BLIND, HAND_UNDERWAY
from rounder.limit import FixedLimit
from rounder.action import SitOut, PostBlind

from rounder.utils import find_action_in_list

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

    def __create_mixed_seats(self):
        """
        Create the following seat structure:

        Seat 0: Player 0, sitting out
        Seat 1: Player 1, sitting in
        Seat 2: Empty
        Seat 3: Player 3, sitting in
        Seat 4: Empty
        Seat 5: Empty
        Seat 6: Player 6, sitting out
        Seat 7: Player 7, sitting in
        Seat 8: Empty
        Seat 9: Empty
        """

        self.seats = Seats(10)
        self.player0 = Player("Player 0")
        self.player1 = Player("Player 1")
        self.player3 = Player("Player 3")
        self.player6 = Player("Player 6")
        self.player7 = Player("Player 7")

        self.player0.sit_out()
        self.player6.sit_out()

        self.seats.seat_player(self.player0, 0)
        self.seats.seat_player(self.player1, 1)
        self.seats.seat_player(self.player3, 3)
        self.seats.seat_player(self.player6, 6)
        self.seats.seat_player(self.player7, 7)

    def test_new_dealer(self):
        self.__create_mixed_seats()
        self.seats.new_dealer()
        self.assertEquals(self.player1, self.seats.dealer)

        self.seats.dealer = self.player3
        self.seats.new_dealer()
        self.assertEquals(self.player7, self.seats.dealer)

        self.seats.dealer = self.player7
        self.seats.new_dealer()
        self.assertEquals(self.player1, self.seats.dealer)

def create_table(num_players, dealer_index):
    limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
    table = Table(name="Test Table", limit=limit, seats=10)

    players = []
    for i in range(num_players):
        new_player = Player('player' + str(i), Currency(CHIPS))
        table.seat_player(new_player, i)
        players.append(new_player)

    return (limit, table, players)



class TableTests(unittest.TestCase):

    def __create_table(self, num_players, dealer_index):
        tuple = create_table(num_players, dealer_index)
        self.limit = tuple[0]
        self.table = tuple[1]
        self.players = tuple[2]

    # def test_not_enough_players_to_start_game

    def test_standard_post_blinds(self):
        self.__create_table(3, 0)
        self.table.begin()
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
        self.assertEquals(HAND_UNDERWAY, self.table.gsm.get_current_state())

    def test_small_blind_sitout_three_handed(self):
        self.__create_table(3, 0)
        self.table.begin()

        # Player 1 rejects the small blind and chooses to sit out:
        self.assertEquals(STATE_SMALL_BLIND, self.table.gsm.get_current_state())
        self.assertEquals(2, len(self.players[1].pending_actions))
        self.table.process_action(find_action_in_list(SitOut, 
            self.players[1].pending_actions))
        self.assertEquals(0, len(self.players[1].pending_actions))
        self.assertEquals(True, self.players[1].sitting_out)
        self.assertEquals(None, self.table.small_blind)

        # Player 0 (not 2) becomes the small blind:
        self.assertEquals(STATE_SMALL_BLIND, self.table.gsm.get_current_state())
        self.assertEquals(2, len(self.players[0].pending_actions))
        self.table.process_action(find_action_in_list(PostBlind, 
            self.players[0].pending_actions))
        self.assertEquals(0, len(self.players[0].pending_actions))
        self.assertEquals(self.players[0], self.table.small_blind)

        # Player 2 should be the big blind:
        self.assertEquals(STATE_BIG_BLIND, self.table.gsm.get_current_state())
        self.assertEquals(None, self.table.big_blind)
        self.assertEquals(2, len(self.players[2].pending_actions))
        self.table.process_action(find_action_in_list(PostBlind, 
            self.players[2].pending_actions))
        self.assertEquals(0, len(self.players[2].pending_actions))
        self.assertEquals(self.players[2], self.table.big_blind)

    def test_big_blind_sitout_three_handed(self):
        self.__create_table(3, 0)
        self.table.begin()
        self.assertEquals(self.players[0], self.table.dealer)

        # Player 1 posts small blind:
        self.table.process_action(find_action_in_list(PostBlind, 
            self.players[1].pending_actions))
        self.assertEquals(self.players[1], self.table.small_blind)

        # Player 2 refuses the big blind:
        self.assertEquals(STATE_BIG_BLIND, self.table.gsm.get_current_state())
        self.table.process_action(find_action_in_list(SitOut, 
            self.players[2].pending_actions))
        self.assertEquals(None, self.table.small_blind)
        self.assertEquals(STATE_SMALL_BLIND, self.table.gsm.get_current_state())
        self.assertEquals(2, len(self.players[0].pending_actions))

    def test_heads_up_blinds(self):
        # Dealer should be the small blind in a heads up match:
        self.__create_table(2, 0)
        self.table.begin()

        self.table.process_action(find_action_in_list(PostBlind, 
            self.players[0].pending_actions))
        self.assertEquals(self.players[0], self.table.small_blind)

        self.table.process_action(find_action_in_list(PostBlind, 
            self.players[1].pending_actions))
        self.assertEquals(self.players[1], self.table.big_blind)

    def test_heads_up_small_blind_sitout(self):
        self.__create_table(2, 0)
        self.table.begin()

        # Player 0 refuses the small blind:
        self.table.process_action(find_action_in_list(SitOut, 
            self.players[0].pending_actions))
        self.assertEquals(None, self.table.gsm.current)
        self.assertEquals(self.players[0], self.table.dealer)
        self.assertEquals(None, self.table.small_blind)
        self.assertEquals(None, self.table.big_blind)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TableTests))
    suite.addTest(unittest.makeSuite(SeatsTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
