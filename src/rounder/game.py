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

from rounder.action import SitOut, Call, Raise, Fold
from rounder.core import RounderException, NotImplementedException
from rounder.deck import Deck
from rounder.currency import Currency

GAME_ID_COUNTER = 1

STATE_PREFLOP = "preflop"
STATE_FLOP = "flop"

def find_next_to_act(players, last_actor_position, bets_this_round, 
    bet_to_match):
    """
    Return the next player to act, or None if this round of betting
    is over.

    players = List of players.
    last_actor_position = List index of last player to act.
    bets_this_round = map of player to amount contributed in this round of
        betting
    bet_to_match = Pretty self explanitory.
    """
    next_to_act = None
    logger.debug("find_next_to_act")
    for i in range(len(players)):
        p = players[(last_actor_position + 1 + i) % len(players)]
        logger.debug("   checking: %s" % str(p))
        logger.debug("      folded = %s" % p.folded)
        logger.debug("      bet so far = %s" % bets_this_round[p])
        logger.debug("      to match = %s" % bet_to_match)
        if not p.folded and bets_this_round[p] < bet_to_match:
            next_to_act = p
            break

    logger.debug("next to act: %s" % str(p))

    return next_to_act

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
        """
        Constructor expects the list of players to all be active, no one
        sitting out.
        """
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
        # Shouldn't be called on the base class.
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

    """ Texas Hold'em, the Cadillac of poker. """

    def __init__(self, limit, players, dealer_index, sb_index, bb_index, 
        callback):
        """
        Blind indicies indicate players who have agreed to post the blinds for
        this hand, thus we can immediately retrieve them and get underway.
        """

        Game.__init__(self, players, callback)

        self.limit = limit
        self.dealer = self.players[dealer_index]
        self.small_blind = self.players[sb_index]
        self.big_blind = self.players[bb_index]

        # Members for tracking the current round of betting:
        self.__last_actor = None
        self.__bet_to_match = None
        self.__in_pot_this_betting_round = {}
        for p in self.players:
            self.__in_pot_this_betting_round[p] = Currency(0.00)

        logger.info("Starting new TexasHoldemGame: " + str(self.id))
        logger.info("   Limit: " + str(limit))
        logger.info("   Players:")
        self.__positions = {} # TODO: Might need a better way to track seats
        i = 0
        for p in self.players:
            code = ''
            if p == self.dealer:
                code += 'dealer '
            if p == self.small_blind:
                code += 'sb '
            if p == self.big_blind:
                code += 'bb '
            logger.info("      %s %s", p, code)
            self.__positions[p] = i
            i += 1

        # Map player to their pending actions. Players are popped as they act
        # so an empty map means no pending actions and we're clear to advance
        # to the next state.
        # TODO: Looking like there's never more than one player with pending
        # actions...
        self.pending_actions = {}

        self.__deck = Deck()
        self.__deck.shuffle()

        self.gsm = GameStateMachine()
        self.gsm.add_state(STATE_PREFLOP, self.preflop)
        self.gsm.add_state(STATE_FLOP, self.flop)
        self.advance()

    def preflop(self):
        """ Initiate preflop game state. """
        self.__collect_blinds()
        self.__deal_hole_cards()
        self.__continue_betting_round()

    def __collect_blinds(self):
        logger.info("Collecting small blind of %s from %s", 
            self.limit.small_blind, self.small_blind.name)
        self.add_to_pot(self.small_blind, self.limit.small_blind)
        logger.info("Collecting big blind of %s from %s", 
            self.limit.big_blind, self.big_blind.name)
        self.add_to_pot(self.big_blind, self.limit.big_blind)
        logger.info("Pot is now: %s", self.pot)

        self.__last_actor = self.big_blind
        self.__bet_to_match = self.limit.big_blind

    def __deal_hole_cards(self):
        """ Deal 2 cards face down to each player. """
        for p in self.players:
            p.cards.append(self.__deck.draw_card())
        for p in self.players:
            p.cards.append(self.__deck.draw_card())

    def __continue_betting_round(self):
        """
        Check if all players have either folded or contributed their share to
        the pot. If not, find the next to act and prompt them. If so, advance
        the game state.
        """
        # TODO: handle all-ins
        last_actor_position = self.__positions[self.__last_actor]
        next_to_act = find_next_to_act(self.players, last_actor_position,
            self.__in_pot_this_betting_round, self.__bet_to_match)
        if next_to_act is not None:
            # Build the actions we'll present to the player:

            # Set the bet level to 1 on preflop and on the flop, 2 otherwise:
            if self.gsm.get_current_state() == STATE_PREFLOP or \
                self.gsm.get_current_state() == STATE_FLOP:
                bet_level = 1
            else:
                bet_level = 2

            options = self.limit.create_actions(next_to_act, 
                self.__bet_to_match, bet_level)
            self.prompt_player(next_to_act, options)
            return

        logger.debug("Betting round complete.")
        self.advance()

    def flop(self):
        """
        Deal the flop and initiate the betting.
        """
        pass

    def add_to_pot(self, player, amount):
        """ 
        Adds the specified amount to the pot. Handles adjustment of players
        stack as well as internal tracking of who has contributed what.
        """
        player.subtract_chips(amount)
        self.pot = self.pot + amount
        self.in_pot[player] = self.in_pot[player] + amount
        self.__in_pot_this_betting_round[player] = \
            self.__in_pot_this_betting_round[player] + amount
        logger.debug("Adding " + str(amount) + " from " + str(player) + 
            " to pot: " + str(self.pot))

    def prompt_player(self, player, actions_list):
        """ Prompt the given player with the given list of actions. """
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
            logger.warn("PostBlind action received while game underway.")

        if isinstance(action, SitOut):
            pass

        # Remove this player from the pending actions map:
        self.pending_actions.pop(action.player)
        action.player.clear_pending_actions()

        # TODO: continue betting round
        #self.advance()

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

