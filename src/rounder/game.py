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

GAME_ID_COUNTER = 1

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
            raise RounderException("Cannot add states after machine has been started.")

        self.states.append(state_name)
        self.actions[state_name] = action

    def advance(self):
        """
        Advance to the next state and call the approriate callback.
        """
        if self.current == None:
            self.current = 0
        else:
            self.current = self.current + 1
        if self.current >= len(self.states):
            raise RounderException("Attempted to advance beyond configured states.")

        # Execute the callback method for this state:
        self.actions[self.states[self.current]]()



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
    # TODO: map pending player actions

    def __init__(self, limit, players, dealer):
        Game.__init__(self)
        self.limit = limit
        self.players = players
        self.dealer = dealer

        # Map player to their pending actions. Players are popped as they act
        # so an empty map means no pending actions.
        self.pending_actions = {}

    def start(self):
        pass

    def post_blinds(self):
        blind_seats = self.__calculate_blind_seats()
        post_sb = PostBlind(self, blind_seats[0], self.limit.small_blind)
        post_bb = PostBlind(self, blind_seats[1], self.limit.big_blind)
        self.prompt_player(blind_seats[0], [post_sb])
        self.prompt_player(blind_seats[1], [post_bb])

    # TODO: candidate for pushing up to parent class
    def prompt_player(self, player, actions_list):

        """
        Send a list of possible actions to a player and maintain our map
        of requests for action that remain unanswered.
        """

        if (self.pending_actions.has_key(player)):
            # Shouldn't happen, but just in case:
            logger.error("Error adding pending actions for player: " +
                str(player))
            logger.error("   Pre-existing pending actions: " +
                str(self.pending_actions[player]))
            raise RounderException("Pending actions already exist")

        self.pending_actions[player] = actions_list
        player.prompt(actions_list)

    def __calculate_blind_seats(self):
        return (self.players[self.dealer + 1], self.players[self.dealer + 2])

    def perform(self, action):
        logger.info("ACTION: " + str(action))

        # TODO: validate
        
        # TODO: Clean this up:
        if isinstance(action, PostBlind):
            action.player.chips = action.player.chips - action.amount

    def __advance_game(self):
        """ 
        Check if we no longer have any actions pending and advance the
        game state if so. 
        """
        pass

