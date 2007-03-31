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

""" The Rounder Game Module """

from logging import getLogger
logger = getLogger("rounder.game")

from rounder.action import *
from rounder.core import *
from rounder.deck import Deck

GAME_ID_COUNTER = 1

STATE_SMALL_BLIND = "small_blind"
STATE_BIG_BLIND = "big_blind"
STATE_PREFLOP = "preflop"

class GameStateMachine:

    """ 
    State machine to represent the current game state. Game instances
    create a state machine and populate it with various states, each
    of which maps to a method to be called when transitioning into
    that state.
    """

    def __init__(self):
        # List of strings representing the state transitions:
        self.states = []

        # Pointer to current state:
        self.current = None

        # Map of state name to callback method:
        self.actions = {}

    def add_state(self, state_name, action):
        """
        Add the given state and method to call when transitioning into it.
        """

        # Can't add states after the machine has been started:
        if self.current != None:
            raise RounderException("Cannot add states after machine has " +
                "been started.")

        self.states.append(state_name)
        self.actions[state_name] = action

    def advance(self):
        """
        Advance to the next state and call the appropriate callback.
        """
        if self.current == None:
            self.current = 0
        else:
            self.current = self.current + 1
        if self.current >= len(self.states):
            raise RounderException("Attempted to advance beyond configured " +
                "states.")

        logger.debug("Advancing to state: " + self.states[self.current])

        # Execute the callback method for this state:
        self.actions[self.states[self.current]]()

    def get_current_state(self):
        return self.states[self.current]



class Game:

    """ Parent class of all poker games. """

    def __init__(self):
        # Every hand played needs a unique ID:
        self.id = ++GAME_ID_COUNTER

    def start(self):
        """ Begin the hand. """
        raise NotImplementedException()

    def perform(self, action):
        """ 
        Perform a player action.

        Assume that any parameters required for the action have already
        been received from the player, parsed, and applied to the action.

        NOTE: Be sure to validate the incoming action exists (i.e. we have
        a record of sending this action to the player) and we validate
        the parameters returned from the player. (to prevent users from
        modifying the client source and returning bogus actions)
        """
        raise NotImplementedException()
        


class TexasHoldemGame(Game):

    """ Texas Hold'em, the king of all poker games. """

    def __init__(self, limit, players, dealer):
        Game.__init__(self)
        self.limit = limit
        self.dealer = dealer

        # List of players passed in should have empty seats and players
        # sitting out filtered out:
        self.players = players

        # Pointers to the position in the players list that has accepted the
        # small and big blind, initially nobody:
        self.small_blind = None
        self.big_blind = None

        logger.info("Starting new TexasHoldemGame: " + str(self.id))
        logger.info("   Limit: " + str(limit))
        logger.info("   Players:")
        for p in self.players:
            logger.info("      " + p.name)

        # Map player to their pending actions. Players are popped as they act
        # so an empty map means no pending actions and we're clear to advance
        # to the next state.
        # TODO: Looking like there's never more than one player with pending
        # actions...
        self.pending_actions = {}

        self.__deck = Deck()
        self.__deck.shuffle()

        self.gsm = GameStateMachine()
        self.gsm.add_state(STATE_SMALL_BLIND, self.prompt_small_blind)
        self.gsm.add_state(STATE_BIG_BLIND, self.prompt_big_blind)
        self.gsm.add_state(STATE_PREFLOP, self.deal_hole_cards)

    def prompt_small_blind(self):
        logger.debug("posting small blind")

        # Modulus to handle wrapping around the end of the list:
        self.small_blind = (self.dealer + 1) % len(self.players)

        post_sb = PostBlind(self, self.players[self.small_blind], 
            self.limit.small_blind)
        sit_out = SitOut(self, self.players[self.small_blind])
        self.prompt_player(self.players[self.small_blind], [post_sb, sit_out])

    def prompt_big_blind(self):
        logger.debug("posting big blind")

        # Modulus to handle wrapping around the end of the list:
        self.big_blind = (self.dealer + 2) % len(self.players)

        post_bb = PostBlind(self, self.players[self.big_blind], 
            self.limit.big_blind)
        sit_out = SitOut(self, self.players[self.big_blind])
        self.prompt_player(self.players[self.big_blind], [post_bb, sit_out])

    def deal_hole_cards(self):
        """ Deal 2 cards face down to each player. """
        for p in self.players:
            p.cards.append(self.__deck.draw_card())
        for p in self.players:
            p.cards.append(self.__deck.draw_card())

    def prompt_player(self, player, actions_list):
        if (self.pending_actions.has_key(player)):
            # Shouldn't happen, but just in case:
            logger.error("Error adding pending actions for player: " +
                str(player))
            logger.error("   Pre-existing pending actions: " +
                str(self.pending_actions[player]))
            raise RounderException("Pending actions already exist")
        self.pending_actions[player] = actions_list

        player.prompt(actions_list)

    def perform(self, action):
        logger.info("Incoming action: " + str(action))

        # TODO: verify the action coming back has valid params?
        # TODO: asserting the player responding to the action actually was
        #   given the option, perhaps at another layer (server?)
        
        # TODO: Clean this up:
        if isinstance(action, PostBlind):
            action.player.chips = action.player.chips - action.amount
        if isinstance(action, SitOut):
            # SitOut actions should only be received while gathering blinds:
            if self.gsm.get_current_state() == STATE_SMALL_BLIND:
                logger.info("Sitting player out: " + str(action.player))
                # Remove the player from the game and rerequest the small blind:
                # TODO: should we check that the player is in the list?
                self.players.remove(action.player)
                self.prompt_small_blind()
            if self.gsm.get_current_state() == STATE_BIG_BLIND:
                logger.info("Sitting player out: " + str(action.player))
                # Remove the player from the game and rerequest the big blind:
                self.players.remove(action.player)
                self.prompt_big_blind()

        # Remove this player from the pending actions map:
        self.pending_actions.pop(action.player)

        # Check if any actions are still pending, and if not advance the game:
        self.advance()

    def advance(self):
        """ 
        Check if we no longer have any actions pending and advance the
        game state if possible.
        """
        if len(self.pending_actions.keys()) == 0:
            logger.debug("No actions pending, advancing game.")
            self.gsm.advance()

        else:
            logger.debug("Actions still pending:")
            for p in self.pending_actions.keys():
                logger.debug("   " + p.name + " " + str(self.pending_actions[p]))

