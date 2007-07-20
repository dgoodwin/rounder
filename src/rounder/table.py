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

""" The Rounder Table Module """

from logging import getLogger
logger = getLogger("rounder.table")

from rounder.action import PostBlind, SitOut
from rounder.core import RounderException
from rounder.game import GameStateMachine, TexasHoldemGame
from rounder.utils import find_action_in_list

STATE_SMALL_BLIND = "small_blind"
STATE_BIG_BLIND = "big_blind"
HAND_UNDERWAY = "hand_underway"

MIN_PLAYERS_FOR_HAND = 2

# Incremented every time a new table is created. Likely to be replaced with
# a database auto-increment down the road.
table_id_counter = 0

class Seats(object):
    """ 
    Data structure to manage players seated at the table.
    Tracks the dealer, small blind, big blind, and provides convenience
    functionality for navigating taking into account who is sitting out.
    """

    def __init__(self, num_seats=10):
        self.__seats = [None] * num_seats
        self.dealer = None
        self.small_blind = None
        self.big_blind = None

    def get_size(self):
        return len(self.__seats)

    def seat_player(self, player, seat_number):
        if seat_number < 0:
            raise RounderException("Invalid seat number: " + str(seat_number))
        if seat_number >= len(self.__seats):
            raise RounderException("Invalid seat number: " + str(seat_number))
        if self.__seats[seat_number] != None:
            raise RounderException("Seat already occupied: " + str(seat_number))

        # Ensure a player can't get seated twice at one table:
        for seat in self.__seats:
            if seat != None:
                if seat.name == player.name:
                    raise RounderException("%s already seated at table" %
                        (player.name))

        self.__seats[seat_number] = player
        player.seat = seat_number

    def get_player(self, seat_number):
        return self.__seats[seat_number]

    def __get_active_players(self):    
        active_players = []
        for p in self.__seats:
            if p != None and not p.sitting_out:
                active_players.append(p)
        return active_players
    active_players = property(__get_active_players, None)

    def __get_first_active_seat(self, start_at):
        """ 
        Returns the next seat index occupied by a player who isn't
        sitting out, starting at the given index. 
        """
        for i in range(len(self.__seats)):
            seat_num = int((i + start_at) % len(self.__seats))
            player = self.get_player(seat_num)
            if player != None and not player.sitting_out:
                return seat_num

    def new_dealer(self):
        """ Select a new dealer. """
        logger.debug("Selecting new dealer.")
        if self.dealer == None:
            self.dealer = self.__seats[self.__get_first_active_seat(0)]
        else:
            self.dealer = self.__seats[self.__get_first_active_seat(
                (self.dealer.seat + 1) % len(self.__seats))]
        logger.debug("New dealer: %s" % self.dealer)

    def small_blind_to_prompt(self):
        """ 
        Return the next appropriate player for prompting the small blind. 
        May be called multiple times in the event we prompt and the player
        chooses to sit out rather than post.
        """
        if self.small_blind != None:
            raise RounderException("Small blind already defined: %s" % 
                self.get_player(self.__small_blind_index))

        if self.dealer == None:
            raise RounderException("Need a dealer before small blind.")

        if len(self.active_players) == 2:
            # Dealer is the small blind heads up:
            return self.dealer

        start_at = (self.dealer.seat + 1) % len(self.__seats)
        return self.__seats[self.__get_first_active_seat(start_at)]

    def big_blind_to_prompt(self):
        """ 
        Return the next appropriate player for prompting the big blind. 
        May be called multiple times in the event we prompt and the player
        chooses to sit out rather than post.
        """
        if self.big_blind != None:
            raise RounderException("Big blind already defined: %s" % 
                self.get_player(self.__big_blind_index))

        if self.dealer == None:
            raise RounderException("Need a dealer before big blind.")

        if len(self.active_players) == 2:
            start_at = (self.dealer.seat + 1) % len(self.__seats)
        else:
            start_at = (self.dealer.seat + 2) % len(self.__seats)

        return self.__seats[self.__get_first_active_seat(start_at)]



class Table(object):

    """ 
    Representation of a table at which a poker game is taking place.
    """

    def __init__(self, name, limit, seats=10, game_over_callback=None):
        global table_id_counter
        table_id_counter += 1
        self.id = table_id_counter

        self.name = name
        self.limit = limit
        self.seats = Seats(num_seats=seats)

        self.gsm = GameStateMachine()
        self.gsm.add_state(STATE_SMALL_BLIND, self.prompt_small_blind)
        self.gsm.add_state(STATE_BIG_BLIND, self.prompt_big_blind)
        self.gsm.add_state(HAND_UNDERWAY, self.__begin_hand)
        logger.info("Created table: %s" % self)

        self.observers = []
        self.game = None

        # Action is typically driven by a parent object who decides when there
        # are enough players seated at the table to begin a game, as well as 
        # when a new hand should be started after one has finished. While 
        # requests to sit will normally filter in through the parent object,
        # it will need a callback to signal when a hand has been completed 
        # at a particular table:
        self.game_over_callback = game_over_callback

    def __repr__(self):
        return "%s (#%s)" % (self.name, self.id)

    def begin(self):
        """ 
        Select a new dealer and prompt for players to agree to post
        their blinds. Once we receive the appropriate responses the hand
        will be started. 

        Intended to be called by a parent object, usually a server.
        """
        if len(self.seats.active_players) < MIN_PLAYERS_FOR_HAND:
            raise RounderException(
                "Table %s: %s players required to begin hand." %
                (self.id, MIN_PLAYERS_FOR_HAND))
        self.seats.new_dealer()
        if self.gsm.current == None:
            self.gsm.advance()

    @staticmethod
    def __find_players_index(player_list, player):
        """ This needs to go... """
        i = 0
        for p in player_list:
            if p.name == player.name:
                return i
            i += 1
        return None

    def __begin_hand(self):
        """ 
        GameStateMachine callback to actually begin a game.
        """
        logger.info("Table %s: New game starting" % self.id)
        active_players = self.seats.active_players

        dealer_index = self.__find_players_index(active_players, 
                self.seats.dealer)
        sb_index = self.__find_players_index(active_players, 
                self.small_blind)
        bb_index = self.__find_players_index(active_players, 
                self.big_blind)

        self.game = TexasHoldemGame(limit=self.limit, 
            players=self.seats.active_players, dealer_index=dealer_index, 
            sb_index=sb_index, bb_index=bb_index,
            callback=self.game_over_callback)

    def game_over(self):
        """ Called by a game when it has finished. """
        logger.debug("Table %s: Game over" % self.id)
        if self.game_over_callback != None:
            self.game_over_callback()

    def __restart(self):
        """
        Restarts the action at this table. Mostly just useful in the event
        we're three handed and the big blind sits out, requiring that we
        find a new small blind.
        """
        logger.debug("Table %s: Restarting hand" % self.id)
        # TODO: exception if game is already underway
        self.small_blind = None
        self.big_blind = None
        self.gsm.reset()
        self.gsm.advance()

    def wait(self):
        """ 
        Put the table on hold while we wait for more players. 

        Parent will normally restart the action. Should never be called when
        a hand is already underway.
        """
        logger.info("Table %s: Waiting for more players.")
        self.gsm.reset()
        self.small_blind = None
        self.big_blind = None
        self.game = None

    def seat_player(self, player, seat_num):
        self.seats.seat_player(player, seat_num)
        player.table = self
        logger.debug("Table %s: %s took seat %s" % (self.id, player.name,
            seat_num))

    def prompt_small_blind(self):
        """
        Prompt the small blind to agree to post. No chips actually change
        hands here, but the table is responsible for finding the two players
        who agree to post the blinds to pass into the next game played. The
        game itself is responsible for collecting those blinds.
        """
        sb = self.seats.small_blind_to_prompt()
        logger.debug("Table %s: Requesting small blind from: %s" % (self.id,
            sb.name))
        post_sb = PostBlind(sb, self.limit.small_blind)
        sit_out = SitOut(sb)
        self.prompt_player(sb, [post_sb, sit_out])

    @staticmethod
    def prompt_player(player, actions_list):
        #self.pending_actions[player] = actions_list
        player.prompt(actions_list)

    def prompt_big_blind(self):
        """
        Prompt the big blind to agree to post. No chips actually change
        hands here, but the table is responsible for finding the two players
        who agree to post the blinds to pass into the next game played. The
        game itself is responsible for collecting those blinds.
        """

        # If heads-up, non-dealer becomes the big blind:
        bb = self.seats.big_blind_to_prompt()
        logger.debug("Table %s: Requesting big blind from: %s" % (self.id,
            bb.name))
        post_bb = PostBlind(bb, self.limit.big_blind)
        sit_out = SitOut(bb)
        self.prompt_player(bb, [post_bb, sit_out])


    def process_action(self, action):
        logger.info("Table %s: Incoming action: %s" % (self.id, action))
        p = action.player

        # TODO: verify the action coming back has valid params?
        # TODO: asserting the player responding to the action actually was
        #   given the option, perhaps at another layer (server?)
        
        pending_actions_copy = []
        pending_actions_copy.extend(p.pending_actions)
        p.clear_pending_actions()

        # TODO: Clean this up:
        if isinstance(action, PostBlind):
            if self.gsm.get_current_state() == STATE_SMALL_BLIND:
                self.small_blind = p
                self.gsm.advance()
            elif self.gsm.get_current_state() == STATE_BIG_BLIND:
                self.big_blind = p
                self.gsm.advance()

        elif isinstance(action, SitOut):

            logger.info("Table %s: Sitting player out: %s" % (self.id, p))
            p.sit_out()

            if len(self.seats.active_players) < MIN_PLAYERS_FOR_HAND:
                # TODO: fishy, might need some work, suspect this is going
                # to interfere with hands underway.
                logger.debug("Table %s: Not enough players for a new hand." %
                    (self.id))
                self.wait()

            if find_action_in_list(PostBlind, pending_actions_copy) != None \
                and self.gsm.get_current_state() == STATE_SMALL_BLIND:
                p.sit_out()
                self.prompt_small_blind()

            if find_action_in_list(PostBlind, pending_actions_copy) != None \
                and self.gsm.get_current_state() == STATE_BIG_BLIND:
                p.sit_out()
                if len(self.seats.active_players) == 2:
                    # if down to heads up, we need a different small blind:
                    self.__restart()
                self.prompt_big_blind()

    # Setup two properties for the small and big blinds, which are actually
    # stored on the tables seat object.
    def __get_small_blind(self):
        return self.seats.small_blind 

    def __set_small_blind(self, small_blind):
        self.seats.small_blind = small_blind
    small_blind = property(__get_small_blind, __set_small_blind)

    def __get_big_blind(self):
        return self.seats.big_blind 

    def __set_big_blind(self, big_blind):
        self.seats.big_blind = big_blind
    big_blind = property(__get_big_blind, __set_big_blind)

    def __get_dealer(self):
        return self.seats.dealer
    dealer = property(__get_dealer, None)

    def notify_player_seated(self):
        """ Notify observers of this table that a player was seated. """
        for o in self.observers:
            o.notify_player_seated

    def game_underway(self):
        """ Return True if there's currently a game underway at this table. """
        if self.gsm.get_current_state() == HAND_UNDERWAY:
            return True
        return False
