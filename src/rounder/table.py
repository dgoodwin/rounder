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
from rounder.game import GameStateMachine
from rounder.utils import find_action_in_list

STATE_SMALL_BLIND = "small_blind"
STATE_BIG_BLIND = "big_blind"
HAND_UNDERWAY = "hand_underway"

MIN_PLAYERS_FOR_HAND = 2

class Seats:
    """ 
    Data structure to manage players seated at the table.
    Tracks the dealer, small blind, big blind, and provides convenience
    functionality for navigating taking into account who is sitting out.
    """

    def __init__(self, num_seats=10):
        self.__seats = []
        for i in range(num_seats):
            self.__seats.append(None)

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

        if self.dealer== None:
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

        if self.dealer== None:
            raise RounderException("Need a dealer before big blind.")

        if len(self.active_players) == 2:
            start_at = (self.dealer.seat + 1) % len(self.__seats)
        else:
            start_at = (self.dealer.seat + 2) % len(self.__seats)

        return self.__seats[self.__get_first_active_seat(start_at)]



class Table:

    """ 
    Representation of a table at which a poker game is taking place.
    """

    def __init__(self, name, limit, seats=10):
        self.limit = limit
        self.seats = Seats(num_seats=seats)
        self.name = name

        self.gsm = GameStateMachine()
        self.gsm.add_state(STATE_SMALL_BLIND, self.prompt_small_blind)
        self.gsm.add_state(STATE_BIG_BLIND, self.prompt_big_blind)
        self.gsm.add_state(HAND_UNDERWAY, self.__begin_hand)

    def __repr__(self):
        return self.name

    def begin(self):
        """ 
        Select a new dealer and prompt for players to agree to post
        their blinds. Once we receive the appropriate responses the hand
        will be started. 
        """
        self.seats.new_dealer()
        if self.gsm.current == None:
            self.gsm.advance()

    def __restart(self):
        """
        Restarts the action at this table. Mostly just useful in the event
        we're three handed and the big blind sits out, requiring that we
        find a new small blind.
        """
        logger.debug("restarting hand")
        # TODO: exception if game is already underway
        self.small_blind = None
        self.big_blind = None
        self.gsm.reset()
        self.gsm.advance()

    def wait(self):
        """ Put the table on hold while we wait for more players. """
        self.gsm.reset()
        self.small_blind = None
        self.big_blind = None

    def __begin_hand(self):
        pass

    def seat_player(self, player, seat_num):
        self.seats.seat_player(player, seat_num)
        player.table = self

    def prompt_small_blind(self):
        """
        Prompt the small blind to agree to post. No chips actually change
        hands here, but the table is responsible for finding the two players
        who agree to post the blinds to pass into the next game played. The
        game itself is responsible for collecting those blinds.
        """
        sb = self.seats.small_blind_to_prompt()
        logger.debug("requesting small blind from: " + sb.name)
        post_sb = PostBlind(sb, self.limit.small_blind)
        sit_out = SitOut(sb)
        self.prompt_player(sb, [post_sb, sit_out])

    def prompt_player(self, player, actions_list):
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
        logger.debug("requesting big blind from: %s" % bb.name)
        post_bb = PostBlind(bb, self.limit.big_blind)
        sit_out = SitOut(bb)
        self.prompt_player(bb, [post_bb, sit_out])


    def process_action(self, action):
        logger.info("Incoming action: " + str(action))
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

            logger.info("Sitting player out: " + str(p))
            p.sit_out()

            if len(self.seats.active_players) < MIN_PLAYERS_FOR_HAND:
                logger.debug("Not enough players for a new hand.")
                self.wait()

            if find_action_in_list(PostBlind, pending_actions_copy) != None and \
                self.gsm.get_current_state() == STATE_SMALL_BLIND:
                p.sit_out()
                self.prompt_small_blind()

            if find_action_in_list(PostBlind, pending_actions_copy) != None and \
                self.gsm.get_current_state() == STATE_BIG_BLIND:
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
