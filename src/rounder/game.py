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

from pokereval import PokerEval

from rounder.action import Call, Raise, Fold
from rounder.core import RounderException
from rounder.deck import Deck
from rounder.currency import Currency

GAME_ID_COUNTER = 1

STATE_PREFLOP = "preflop"
STATE_FLOP = "flop"
STATE_TURN = "turn"
STATE_RIVER = "river"
STATE_GAMEOVER = "gameover"

def split_pot(pot, winners):
    """ 
    Split the pot up as evenly as possible amongst the list of winners. 

    Potential remaining cent is given to first player in the list.
    """
    logger.info("Splitting pot: " + str(pot))
    per_player = pot / len(winners)
    remainder = pot - (per_player * len(winners))
    logger.debug("remainder = " + str(remainder))
    
    for p in winners:
        winnings = per_player + remainder
        remainder = 0 # only add for the first player in the list
        p.add_chips(winnings)
        logger.info("   %s won %s" % (p.name, winnings))


def find_next_to_act(players, last_actor_position, bets_this_round, 
    bet_to_match, bb_exception=None):
    """
    Return the next player to act, or None if this round of betting
    is over.

    players = List of players.
    last_actor_position = List index of last player to act.
    bets_this_round = Map of player to amount contributed in this round of
        betting. If a player is missing from the map, they haven't yet been
        prompted for anything this round of betting. Used to determine who
        we've prompted in the event the betting is checked around.
    bet_to_match = Pretty self explanitory.
    big_blind_exception = Player who we can assume is the next to act even if
        we process them and find they've already contributed the current bet to
        the pot. Used to handle the odd situation where the big blind can check
        or raise if there hasn't already been a raise preflop.
    """
    logger.debug("find_next_to_act")
    next_to_act = None
    for i in range(len(players)):
        p = players[(last_actor_position + 1 + i) % len(players)]
        if not p.folded: 
            if bet_to_match == 0 and not bets_this_round.has_key(p):
                logger.debug("   1")
                next_to_act = p
                break
            elif bets_this_round.has_key(p) and \
                (bets_this_round[p] < bet_to_match or
                    p == bb_exception):
                logger.debug("   2")
                next_to_act = p
                break
            elif not bets_this_round.has_key(p):
                logger.debug("   3")
                next_to_act = p
                break
            else:
                logger.debug("   skipping %s" % p)
        else:
            logger.debug("   skipping %s" % p)

    logger.debug("next to act: %s" % str(next_to_act))

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



class Game(object):

    """ Parent class of all poker games. """

    def __init__(self, players, callback, table=None):
        """
        Constructor expects the list of players to all be active, no one
        sitting out.
        """
        # Every hand played needs a unique ID:
        self.id = ++GAME_ID_COUNTER

        self.table = table

        # A callback method we can call when this game is finished to return
        # control to the object that created us:
        self.callback = callback

        self.aborted = False
        self.finished = False
        self.winners = None # Player who won this hand

        # List of players passed in should have empty seats and players
        # sitting out filtered out:
        # TODO: check for empty/sitting out spots:
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
        raise NotImplementedError()

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
        raise NotImplementedError()

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

    def _check_if_finished(self):
        """
        Check if we're trying to do anything but the game has already been
        marked as finished.
        """
        if self.finished:
            raise RounderException("Game is finished.")

    def __get_active_players(self):    
        active_players = []
        for p in self.players:
            if not p.folded:
                active_players.append(p)
        return active_players
    active_players = property(__get_active_players, None)

        


class TexasHoldemGame(Game):

    """ Texas Hold'em, the Cadillac of poker. """

    def __init__(self, limit, players, dealer_index, sb_index, bb_index, 
        callback, table=None):
        """
        Blind indicies indicate players who have agreed to post the blinds for
        this hand, thus we can immediately retrieve them and get underway.

        Players list represents only those players who were actively at the table
        AND sitting in when the hand began. Positions in the list are not relative.
        All the game cares about is where they sit in relation to one another.
        """

        Game.__init__(self, players, callback, table)

        self.limit = limit
        self.dealer = self.players[dealer_index]
        self.small_blind = self.players[sb_index]
        self.big_blind = self.players[bb_index]

        # Handle the one-off where the big blind has the choice to raise or
        # check preflop if the pot isn't raised, despite already having
        # contributed the current amount to the pot. (which we normally use
        # to determine when betting for this round is over)
        # Set to None if the pot is raised preflop, or once we progress to the 
        # flop.
        self.big_blind_exception = self.players[bb_index]

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

        self.community_cards = []

        self.__deck = Deck()
        self.__deck.shuffle()

        self.gsm = GameStateMachine()
        self.gsm.add_state(STATE_PREFLOP, self.preflop)
        self.gsm.add_state(STATE_FLOP, self.flop)
        self.gsm.add_state(STATE_TURN, self.turn)
        self.gsm.add_state(STATE_RIVER, self.river)
        self.gsm.add_state(STATE_GAMEOVER, self.game_over)

    def __reset_betting_round_state(self):
        """ 
        Resets any members tracking data for the current round of betting. Can
        be used both when starting a new game or moving on to the next round
        of betting within an existing game.
        """
        logger.debug("Resetting betting round state.")
        self.__last_actor = self.dealer # overridden in __collect_blinds
        self.__bet_to_match = 0
        self.__in_pot_this_betting_round = {}

    def preflop(self):
        """ Initiate preflop game state. """
        self._check_if_finished()
        self.__collect_blinds()
        self.__deal_hole_cards()
        self.__continue_betting_round()

    def __collect_blinds(self):
        """ 
        Collect blinds from the players who agreed to post them. (normally handled
        by the table)
        """

        self._check_if_finished()
        self.add_to_pot(self.small_blind, self.limit.small_blind)
        logger.info("Table %s: %s posts the small blind: %s", 
            self.__get_table_id(), self.small_blind.name, self.limit.small_blind)
        self.add_to_pot(self.big_blind, self.limit.big_blind)
        logger.info("Table %s: %s posts the big blind: %s", 
            self.__get_table_id(), self.big_blind.name, self.limit.big_blind)
        logger.info("Pot is now: %s", self.pot)

        self.__last_actor = self.big_blind
        self.__bet_to_match = self.limit.big_blind

    def __deal_hole_cards(self):
        """ Deal 2 cards face down to each player. """
        self._check_if_finished()
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
        self._check_if_finished()

        logger.debug("active players: %s", len(self.active_players))
        # Check if everyone has folded:
        if len(self.active_players) == 1:
            self.game_over() 
            return

        last_actor_position = self.__positions[self.__last_actor]
        next_to_act = find_next_to_act(self.players, last_actor_position,
            self.__in_pot_this_betting_round, self.__bet_to_match, 
            self.big_blind_exception)
        if next_to_act == self.big_blind_exception:
            self.big_blind_exception = None
        if next_to_act is not None:
            # Build the actions we'll present to the player:

            # Set the bet level to 1 on preflop and on the flop, 2 otherwise:
            if self.gsm.get_current_state() == STATE_PREFLOP or \
                self.gsm.get_current_state() == STATE_FLOP:
                bet_level = 1
            else:
                bet_level = 2

            in_pot = Currency(0)
            if self.__in_pot_this_betting_round.has_key(next_to_act):
                in_pot = self.__in_pot_this_betting_round[next_to_act]
            options = self.limit.create_actions(next_to_act, 
                in_pot, self.__bet_to_match, bet_level)
            self.prompt_player(next_to_act, options)
            return

        logger.debug("Betting round complete.")
        self.advance()

    def __get_table_id(self):
        """ Handy for logger statements."""
        if self.table != None:
            return self.table.id
        return "None"

    def flop(self):
        """
        Deal the flop and initiate the betting.
        """
        logger.debug("Table %s: Dealing the flop." % self.__get_table_id)
        self._check_if_finished()

        self.big_blind_exception = None
        for i in range(3):
            self.community_cards.append(self.__deck.draw_card())

        self.__continue_betting_round()

    def turn(self):
        """ Deal the turn and initiate the betting. """
        self._check_if_finished()
        self.community_cards.append(self.__deck.draw_card())
        self.__continue_betting_round()

    def river(self):
        """ Deal the river and initiate the betting. """
        self._check_if_finished()
        self.community_cards.append(self.__deck.draw_card())
        self.__continue_betting_round()

    def add_to_pot(self, player, amount):
        """ 
        Adds the specified amount to the pot. Handles adjustment of players
        stack as well as internal tracking of who has contributed what.
        """
        self._check_if_finished()
        player.subtract_chips(amount)
        self.pot = self.pot + amount
        self.in_pot[player] = self.in_pot[player] + amount

        if not self.__in_pot_this_betting_round.has_key(player):
            self.__in_pot_this_betting_round[player] = amount
        else:
            self.__in_pot_this_betting_round[player] = \
                self.__in_pot_this_betting_round[player] + amount

    def prompt_player(self, player, actions_list):
        """ Prompt the player with a list of actions. """
        self._check_if_finished()
        if (self.pending_actions.has_key(player)):
            # Shouldn't happen, but just in case:
            logger.error("Error adding pending actions for player: " +
                str(player))
            logger.error("   Pre-existing pending actions: " +
                str(self.pending_actions[player]))
            raise RounderException("Pending actions already exist")
        logger.debug("Prompting %s with actions: %s" % (player.name,
            actions_list))
        self.pending_actions[player] = actions_list

        player.prompt(actions_list)
        if self.table != None:
            self.table.prompt_player(player, actions_list)

    def process_action(self, player, action):
        logger.info("Incoming action: " + str(action))
        self._check_if_finished()

        # TODO: verify the action coming back has valid params?
        # TODO: asserting the player responding to the action actually was
        #   given the option, perhaps at another layer (server?)
        
        if isinstance(action, Call):
            self.add_to_pot(player, action.amount)

        if isinstance(action, Raise):
            if self.gsm.get_current_state() == STATE_PREFLOP:
                self.big_blind_exception = None

            self.__bet_to_match += action.amount
            amount = self.__bet_to_match
            if self.__in_pot_this_betting_round.has_key(player):
                amount -= self.__in_pot_this_betting_round[player]
            self.add_to_pot(player, amount)

        if isinstance(action, Fold):
            player.folded = True

        # Remove this player from the pending actions map:
        self.__last_actor = player
        self.pending_actions.pop(player)
        player.clear_pending_actions()
        self.__continue_betting_round()

    def advance(self):
        """ 
        Check if we no longer have any actions pending and advance the
        game state if possible.
        """
        self._check_if_finished()

        if len(self.pending_actions.keys()) == 0:
            logger.debug("No actions pending, advancing game.")
            self.__reset_betting_round_state()
            self.gsm.advance()

        else:
            logger.debug("Actions still pending:")
            for p in self.pending_actions.keys():
                logger.debug("   " + p.name + " " +
                        str(self.pending_actions[p]))

    def game_over(self):
        """
        Finalize this game and return control to our parent object.
        (usually a table)
        """
        logger.info("Game over.")
        self._check_if_finished()
        self.finished = True
        self.winners = []

        pockets = []
        for p in self.active_players:
            cards = []
            cards.append(str(p.cards[0]).lower())
            cards.append(str(p.cards[1]).lower())
            pockets.append(cards)

        board = []
        for c in self.community_cards:
            board.append(str(c).lower())

        evaluator = PokerEval()
        result = evaluator.winners(game="holdem", pockets=pockets,
            board=board)
        for index in result['hi']:
            self.winners.append(self.active_players[index])

        split_pot(self.pot, self.winners)
        logger.info("Winner: %s" % self.winners[0].name)
        logger.info("   pot: %s" % self.pot)
        logger.info("   winners stack: %s" % self.winners[0].chips)

        for p in self.players:
            p.reset()

        # TODO: safe way to return without building a neverending callstack?
        self.callback()

