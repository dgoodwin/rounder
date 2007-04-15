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

from rounder.action import SitOut
from rounder.core import RounderException, NotImplementedException
from rounder.deck import Deck
from rounder.currency import Currency

GAME_ID_COUNTER = 1

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

    def reset(self):
        logger.debug("Resetting game state machine.")
        self.current = None

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
        if self.current == None:
            return None
        return self.states[self.current]



class Game:

    """ Parent class of all poker games. """

    def __init__(self, players, callback):
        # Every hand played needs a unique ID:
        self.id = ++GAME_ID_COUNTER

        # A callback method we can call when this game is finished to return
        # control to the object that created us:
        self.callback = callback

        self.aborted = False

        # List of players passed in should have empty seats and players
        # sitting out filtered out:
        self.players = players

        # A map of player to amount contributed to the pot, can be used both
        # as a definitive list of all players who were present when this game
        # started (as they're removed from the list when sitting out), as well
        # as a record of how much to refund to each player in the event this
        # game is aborted.
        self.in_pot = {}
        for p in self.players:
            self.in_pot[p] = Currency(0.00)
            
        self.pot = Currency(0.00)

    def start(self):
        """ Begin the hand. """
        raise NotImplementedException()

    def process_action(self, action):
        """ 
        Process a player action.

        Assume that any parameters required for the action have already
        been received from the player, parsed, and applied to the action.

        NOTE: Be sure to validate the incoming action exists (i.e. we have
        a record of sending this action to the player) and we validate
        the parameters returned from the player. (to prevent users from
        modifying the client source and returning bogus actions)
        """
        raise NotImplementedException()

    def abort(self):
        """ 
        Abort the current hand and return control to the object that 
        created us.
        """
        logger.warn("Aborting game:")
        self.aborted = True
        for p in self.players:
            p.clear_pending_actions()
            p.add_chips(self.in_pot[p])
            self.pot = self.pot - self.in_pot[p]
            self.in_pot[p] = Currency(0.00)
        if self.pot > 0:
            logger.error("Funds left in pot after refuding all players: " + 
                str(self.pot))
        self.callback()
        


class TexasHoldemGame(Game):

    """ Texas Hold'em, the king of all poker games. """

    def __init__(self, limit, players, dealer, callback):
        Game.__init__(self, players, callback)
        self.limit = limit
        self.dealer = dealer

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

    def add_to_pot(self, player, amount):
        """ Adds the specified amount to the pot. """
        player.subtract_chips(amount)
        self.pot = self.pot + amount
        self.in_pot[player] = self.in_pot[player] + amount
        logger.debug("Adding " + str(amount) + " from " + str(player) + 
            " to pot: " + str(self.pot))

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

    def process_action(self, action):
        logger.info("Incoming action: " + str(action))

        # TODO: verify the action coming back has valid params?
        # TODO: asserting the player responding to the action actually was
        #   given the option, perhaps at another layer (server?)
        
        # TODO: Clean this up:
        if isinstance(action, PostBlind):
            self.add_to_pot(action.player, action.amount)
            if self.gsm.get_current_state() == STATE_SMALL_BLIND:
                # TODO: Might need a safer way to look for the players seat:
                self.small_blind = self.players.index(action.player)
            if self.gsm.get_current_state() == STATE_BIG_BLIND:
                # TODO: Might need a safer way to look for the players seat:
                self.big_blind = self.players.index(action.player)

        if isinstance(action, SitOut):

            if len(self.players) == 2:
                if self.gsm.get_current_state() == STATE_BIG_BLIND:
                    self.__refund_small_blind()
                self.abort()
                return

            # SitOut actions should only be received while gathering blinds:
            if self.gsm.get_current_state() == STATE_SMALL_BLIND:
                logger.info("Sitting player out: " + str(action.player))
                action.player.sit_out()
                # Remove the player from the game and rerequest the small blind:
                # TODO: should we check that the player is in the list?
                self.players.remove(action.player)
                self.prompt_small_blind()
            if self.gsm.get_current_state() == STATE_BIG_BLIND:
                logger.info("Sitting player out: " + str(action.player))
                action.player.sit_out()
                # Remove the player from the game and rerequest the big blind:
                self.players.remove(action.player)

                # If the big blind just sat out in a three handed game, we've
                # already collected the small blind, but in a heads up hand
                # the dealer is supposed to be the small blind. For now we will
                # cancel the hand to deal with this situation.
                if len(self.players) == 2:
                    action.player.clear_pending_actions()
                    self.abort()
                    return

                self.prompt_big_blind()

        # Remove this player from the pending actions map:
        self.pending_actions.pop(action.player)
        action.player.clear_pending_actions()

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

