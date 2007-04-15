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

from rounder.action import SitOut, PostBlind
from rounder.core import RounderException
from rounder.limit import FixedLimit
from rounder.player import Player
from rounder.game import TexasHoldemGame, GameStateMachine
from rounder.currency import Currency
from rounder.utils import find_action_in_list

CHIPS = 1000

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

    def __create_game(self, numPlayers, dealerIndex):
        self.players = []
        for i in range(numPlayers):
            self.players.append(Player('player' + str(i), 
                Currency(CHIPS)))
        limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))

        # Copy the players list, the game can modify it's own list and we
        # need to maintain the references to the original players:
        players_copy = []
        players_copy.extend(self.players)

        self.game = TexasHoldemGame(limit=limit, players=players_copy, 
            dealer=dealerIndex, callback=self.game_over_callback)
        self.game_over = False

    def test_something(self):
        # At this point, players should be dealt their hole cards:
        for player in self.players:
            self.assertEquals(2, len(player.cards))
        self.assertEquals(CHIPS, self.players[0].chips)

    def test_prompt_player_actions_already_pending(self):
        self.__create_game(3, 0)
        self.game.prompt_small_blind()
        self.assertRaises(RounderException, self.game.prompt_small_blind)

    def test_big_blind_sitout_three_handed(self):
        # Difficult situation here, when down to heads up the dealer should
        # be the small blind, which is incorrect according to the normal
        # means of selecting the small and big blind. If the big blind choses
        # to sit out, we already have processed the small blind, who should now
        # be the dealer. To compensate for this situation we'll canel the hand
        # and allow the table to start a new one with just the heads up 
        # players.
        self.__create_game(3, 0)
        self.game.advance()

        # Player 1 posts small blind:
        self.game.process_action(find_action_in_list(PostBlind, 
            self.players[1].pending_actions))
        self.assertEquals(CHIPS - 1, self.players[1].chips)

        # Player 2 refuses the big blind:
        self.game.process_action(find_action_in_list(SitOut, 
            self.players[2].pending_actions))

        self.assertEquals(True, self.game_over)
        self.assertEquals(True, self.game.aborted)

        self.assertEquals(CHIPS, self.players[1].chips)
        self.assertEquals(CHIPS, self.players[0].chips)
        self.assertEquals(CHIPS, self.players[2].chips)

    def test_heads_up_blinds(self):
        # Dealer should be the small blind in a heads up match:
        self.__create_game(2, 0)
        self.game.advance()

        self.game.process_action(find_action_in_list(PostBlind, 
            self.players[0].pending_actions))
        self.assertEquals(CHIPS - 1, self.players[0].chips)

        self.game.process_action(find_action_in_list(PostBlind, 
            self.players[1].pending_actions))
        self.assertEquals(CHIPS - 2, self.players[1].chips)

    def test_heads_up_small_blind_sitout(self):
        self.__create_game(2, 0)
        self.game.advance()

        # Player 0 refuses the small blind:
        self.game.process_action(find_action_in_list(SitOut, 
            self.players[0].pending_actions))

        self.assertEquals(True, self.game_over)
        self.assertEquals(True, self.game.aborted)
        self.assertEquals(CHIPS, self.players[1].chips)
        self.assertEquals(CHIPS, self.players[0].chips)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TexasHoldemTests))
    suite.addTest(unittest.makeSuite(GameStateMachineTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
