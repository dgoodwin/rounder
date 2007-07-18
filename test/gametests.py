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

from logging import getLogger
logger = getLogger("rounder.test.gametests")

import unittest

import settestpath

from rounder.action import Call, Raise, Fold
from rounder.core import RounderException
from rounder.limit import FixedLimit
from rounder.game import TexasHoldemGame, GameStateMachine, find_next_to_act, \
    split_pot
from rounder.game import STATE_PREFLOP, STATE_FLOP, STATE_TURN, STATE_RIVER, \
    STATE_GAMEOVER
from rounder.currency import Currency
from rounder.utils import find_action_in_list

from utils import create_players_list

CHIPS = 1000

class NextToActTests(unittest.TestCase):

    def setUp(self):
        self.players = create_players_list(10, CHIPS)
        self.bets = {}
        for p in self.players:
            self.bets[p] = Currency(0.00)

    def __set_bet(self, player, amount):
        """
        Adds the specified amount to the pot and subtracts from the players
        stack. 
        """
        self.bets[player] += Currency(amount)
        player.chips -= Currency(amount)

    def test_after_blinds(self):
        self.__set_bet(self.players[1], 1)
        self.__set_bet(self.players[2], 2)

        self.assertEquals(self.players[3], find_next_to_act(self.players, 2, 
            self.bets, 2))

    def test_middle_table(self):
        self.__set_bet(self.players[1], 2)
        self.__set_bet(self.players[2], 2)
        self.__set_bet(self.players[3], 2)
        self.__set_bet(self.players[4], 2)

        self.assertEquals(self.players[5], find_next_to_act(self.players, 4, 
            self.bets, 2))

    def test_wraparound(self):
        self.__set_bet(self.players[9], 2)

        self.assertEquals(self.players[0], find_next_to_act(self.players, 9, 
            self.bets, 2))

    def test_everybody_in(self):
        for p in self.players:
            self.__set_bet(p, 2)
        self.assertEquals(None, find_next_to_act(self.players, 9, self.bets, 2))

    def test_everybody_in_or_folded(self):
        for p in self.players:
            if p.seat < 5:
                self.__set_bet(p, 2)
            else:
                p.folded = True
        self.assertEquals(None, find_next_to_act(self.players, 4, self.bets, 2))

    def test_late_raiser(self):
        for p in self.players:
            if p.seat < 9:
                self.__set_bet(p, 2)
            # seat 9 raises:
            self.__set_bet(self.players[9], 4)
        self.assertEquals(self.players[0], find_next_to_act(self.players, 9,
            self.bets, 4))
            


class GameStateMachineTests(unittest.TestCase):

    def callback(self):
        """ To be called by the state machine. """
        self.called_back = True

    def test_add_state(self):
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        self.assertEquals(1, len(machine.states))
        self.assertEquals("postblinds", machine.states[0])
        self.assertEquals(self.callback, machine.actions["postblinds"])

    def test_first_advance(self):
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        self.assertEquals(None, machine.current)
        machine.advance()
        self.assertEquals(0, machine.current)

    def test_advance(self):
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        machine.add_state("preflop", self.callback)
        machine.add_state("holecards", self.callback)
        machine.add_state("flop", self.callback)
        machine.add_state("turn", self.callback)
        machine.add_state("river", self.callback)
        machine.add_state("done", self.callback)
        self.assertEquals(None, machine.current)
        for i in range(0, 7):
            machine.advance()
            self.assertEquals(i, machine.current)

    def test_advance_too_far(self):
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        self.assertEquals(None, machine.current)
        machine.advance()
        self.assertRaises(RounderException, machine.advance)

    def test_add_state_after_starting(self):
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        machine.advance()
        self.assertRaises(RounderException, machine.add_state, "any", 
            self.callback)

    def test_callback(self):
        self.called_back = False
        machine = GameStateMachine()
        machine.add_state("postblinds", self.callback)
        machine.advance()
        self.assertEquals(True, self.called_back)



class TexasHoldemTests(unittest.TestCase):

    def game_over_callback(self):
        self.game_over = True

    def __create_game(self, num_players, dealer_index, sb_index, bb_index):
        self.players = create_players_list(num_players, CHIPS)
        limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))

        # Copy the players list, the game can modify it's own list and we
        # need to maintain the references to the original players:
        players_copy = []
        players_copy.extend(self.players)

        self.game = TexasHoldemGame(limit=limit, players=players_copy, 
            dealer_index=dealer_index, sb_index=sb_index, bb_index=bb_index,
            callback=self.game_over_callback)

        # Referenced in game over callback for determining that a game ended
        # as expected.
        self.game_over = False

    def test_collect_blinds(self):
        self.__create_game(10, 0, 1, 2)
        self.assertEquals(10, len(self.game.players))
        self.assertEquals(3, self.game.pot)
        self.assertEquals(CHIPS - 1, self.players[1].chips)
        self.assertEquals(CHIPS - 2, self.players[2].chips)

        # At this point, players should be dealt their hole cards:
        for player in self.players:
            self.assertEquals(2, len(player.cards))

    def test_preflop_everybody_in(self):
        self.__create_game(4, 0, 1, 2)

        self.assertEquals(STATE_PREFLOP, self.game.gsm.get_current_state())
        self.__call(self.players[3], 2, CHIPS - 2)

        self.assertEquals(STATE_PREFLOP, self.game.gsm.get_current_state())
        self.__call(self.players[0], 2, CHIPS - 2)

        self.assertEquals(STATE_PREFLOP, self.game.gsm.get_current_state())
        self.__call(self.players[1], 1, CHIPS - 2)
        
        self.assertEquals(STATE_PREFLOP, self.game.gsm.get_current_state())
        self.__call(self.players[2], 0, CHIPS - 2)
        
        # Onward to the flop!
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())

    def test_preflop_big_blind_checks(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())

    def __call(self, player, expected_amount, expected_chips=None):
        self.assertEquals(3, len(player.pending_actions))
        call = find_action_in_list(Call, player.pending_actions)
        self.assertEquals(expected_amount, call.amount)
        self.game.process_action(call)
        if expected_chips:
            self.assertEquals(expected_chips, player.chips)

    def __raise(self, player, amount, expected_chips):
        self.assertEquals(3, len(player.pending_actions))
        raise_action = find_action_in_list(Raise, player.pending_actions)
        self.assertEquals(None, raise_action.amount)
        raise_action.validate([amount])
        self.game.process_action(raise_action)
        self.assertEquals(amount, raise_action.amount)
        self.assertEquals(expected_chips, player.chips)

    def __fold(self, player, expected_chips):
        self.assertEquals(3, len(player.pending_actions))
        fold = find_action_in_list(Fold, player.pending_actions)
        self.game.process_action(fold)
        self.assertEquals(expected_chips, player.chips)

    def test_preflop_fold_to_big_blind(self):
        self.__create_game(4, 0, 1, 2)
        self.__fold(self.players[3], CHIPS)
        self.__fold(self.players[0], CHIPS)
        self.__fold(self.players[1], CHIPS - 1)
        self.assertTrue(self.game.finished)
        self.assertTrue(self.game_over)
        self.assertEquals(3, self.game.pot)
        self.assertEquals(CHIPS + 1, self.players[2].chips)

    def test_flop_checked_around(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())
        self.assertEquals(3, len(self.game.community_cards))

        self.__call(self.players[1], 0, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.__call(self.players[3], 0, CHIPS - 2)
        self.__call(self.players[0], 0, CHIPS - 2)
        self.assertEquals(STATE_TURN, self.game.gsm.get_current_state())

    def test_flop_betting(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())
        self.assertEquals(3, len(self.game.community_cards))
    
        self.__raise(self.players[1], 2, CHIPS - 4)
        self.__call(self.players[2], 2, CHIPS - 4)
        self.__raise(self.players[3], 2, CHIPS - 6)
        self.__call(self.players[0], 4, CHIPS - 6)
        self.__raise(self.players[1], 2, CHIPS - 8)
        self.__call(self.players[2], 4, CHIPS - 8)
        self.__raise(self.players[3], 2, CHIPS - 10)
        self.__call(self.players[0], 4, CHIPS - 10)
        self.__call(self.players[1], 2, CHIPS - 10)
        self.__call(self.players[2], 2, CHIPS - 10)

        self.assertEquals(40, self.game.pot)
        self.assertEquals(STATE_TURN, self.game.gsm.get_current_state())

    def test_flop_betting_with_raises_and_folds(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())
        self.assertEquals(3, len(self.game.community_cards))

        self.__raise(self.players[1], 2, CHIPS - 4)
        self.__call(self.players[2], 2, CHIPS - 4)
        self.__fold(self.players[3], CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 4)

        self.assertEquals(14, self.game.pot)
        self.assertEquals(STATE_TURN, self.game.gsm.get_current_state())

    def test_hand_ends_on_flop(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)

        # Flop:
        self.__raise(self.players[1], 2, CHIPS - 4)
        self.__fold(self.players[2], CHIPS - 2)
        self.__fold(self.players[3], CHIPS - 2)
        self.__fold(self.players[0], CHIPS - 2)

        self.assertTrue(self.game.finished)
        self.assertTrue(self.game_over)
        self.assertEquals(10, self.game.pot)
        self.assertEquals(CHIPS + 6, self.players[1].chips)

    def test_full_hand_betting(self):
        self.__create_game(4, 0, 1, 2)
        self.__call(self.players[3], 2, CHIPS - 2)
        self.__call(self.players[0], 2, CHIPS - 2)
        self.__call(self.players[1], 1, CHIPS - 2)
        self.__call(self.players[2], 0, CHIPS - 2)
        self.assertEquals(STATE_FLOP, self.game.gsm.get_current_state())
        self.assertEquals(3, len(self.game.community_cards))
    
        self.__raise(self.players[1], 2, CHIPS - 4)
        self.__call(self.players[2], 2, CHIPS - 4)
        self.__call(self.players[3], 2, CHIPS - 4)
        self.__call(self.players[0], 2, CHIPS - 4)

        self.assertEquals(16, self.game.pot)
        self.assertEquals(STATE_TURN, self.game.gsm.get_current_state())

        self.__call(self.players[1], 0, CHIPS - 4)
        self.__call(self.players[2], 0, CHIPS - 4)
        self.__call(self.players[3], 0, CHIPS - 4)
        self.__call(self.players[0], 0, CHIPS - 4)
        self.assertEquals(STATE_RIVER, self.game.gsm.get_current_state())

        self.__call(self.players[1], 0)
        self.__call(self.players[2], 0)
        self.__call(self.players[3], 0)
        self.__call(self.players[0], 0)
        self.assertEquals(STATE_GAMEOVER, self.game.gsm.get_current_state())
        self.assertTrue(self.game.finished)
        self.assertEquals(16, self.game.pot)

        # TODO check that there was a winner and they received the pot?
        self.assertTrue(len(self.game.winners) > 0)



class SplitPotTests(unittest.TestCase):

    def test_simple_case(self):
        self.players = create_players_list(4, 0)
        pot = Currency(10)
        split_pot(pot, [self.players[0]])
        self.assertEquals(10, self.players[0].chips)

    def test_even_split_case(self):
        self.players = create_players_list(4, 0)
        pot = Currency(10)
        split_pot(pot, self.players[0:2])
        self.assertEquals(5, self.players[0].chips)
        self.assertEquals(5, self.players[1].chips)

    def test_uneven_split_case(self):
        self.players = create_players_list(4, 0)
        pot = Currency(0.25)
        split_pot(pot, self.players[0:2])
        self.assertEquals(0.13, self.players[0].chips)
        self.assertEquals(0.12, self.players[1].chips)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NextToActTests))
    suite.addTest(unittest.makeSuite(GameStateMachineTests))
    suite.addTest(unittest.makeSuite(TexasHoldemTests))
    suite.addTest(unittest.makeSuite(SplitPotTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
