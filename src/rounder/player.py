#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#   Copyright (C) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
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

""" The Rounder Player Module """

from logging import getLogger
from currency import Currency
from rounder.core import InvalidPlay
logger = getLogger("rounder.player")

from rounder.core import RounderException

class Player:

    """
    Player at a poker table. Note one account could be playing at
    multiple tables concurrently, in which case one Player would be
    created for each.
    """

    def __init__(self, username, table=None, seat=None, chips=0):
        self.username = username
        self.chips = chips
        self.table = table
        self.seat = seat
        self.cards = []
        self.sitting_out = False
        self.folded = False
        self.in_hand = False

        # Initialized by new_round:
        self.current_bet = None
        self.raise_round = None
        self.allin = False

        self.reset()

    def reset(self):
        """ Reset player state specific to a hand. """
        self.cards = []
        self.allin = False
        self.current_bet = Currency(0)
        self.final_hand = None
        self.final_hand_rank = None
        self.folded = False
        self.pending_actions = []
        self.new_round()

    def new_round(self):
        """ Called for each new round of betting. """
        amount = self.current_bet
        self.current_bet = Currency(0)
        self.raise_count = -1
        logger.debug("Player bet: " + str(amount))
        return amount

    def can_act(self, raise_count):
        """ Check if the player has another move to make this round. """
        if self.folded or self.allin:
            return False

        if (self.raise_count == raise_count):
            return False

        return True

    def call_bet(self, pot_size, raise_count):
        amount = pot_size - self.current_bet
        if amount > self.chips:
            amount = self.chips

        self.bet(amount, raise_count)

    def bet(self, amount, raise_count):
        """ A bet made by a client. """
        # TODO: Maybe this is too much state for the player to be worried about
        if (amount + self.current_bet == 0 and raise_count > 0    ):
            logger.debug("Client tried to bet 0")
            raise InvalidPlay("Client cannot bet 0")

        # TODO: should this be a better exception?
        assert(raise_count == -1 or self.raise_count != raise_count)

        if (amount > self.chips):
            logger.debug("Client tried to bet more then they had")
            raise InvalidPlay("Client does not have enough chips for that bet")
        elif (amount == self.chips):
            self.allin = True

        self.chips -= amount
        self.current_bet += amount
        self.raise_count = raise_count

    def prompt(self, actions):
        """
        Prompt this player to make a choice among the given actions.

        Returns nothing, but rather an asynchronous call back into the game
        (and perhaps parent objects such as the server) will return the
        players selection.
        """
        self.pending_actions = actions

    def __repr__(self):
        return "Player: %s (seat: %s, chips: %s)" % \
            (self.username, self.seat, self.chips)

    def clear_pending_actions(self):
        """ Clear any actions pending for this player. """
        logger.debug("Clearing pending actions: " + str(self.pending_actions))
        self.pending_actions = []

    def sit_out(self):
        """ Sit player out of the game. """
        self.clear_pending_actions()
        self.sitting_out = True

    def sit_in(self):
        """ Sit player back in the game. """
        self.sitting_out = False

    def add_chips(self, amount):
        """ Add chips to the players stack. """
        if amount < 0:
            raise RounderException("Negative amount, use subtract_chips instead.")
        logger.debug("Adding chips to " + str(self.username) + ": " + str(amount))
        self.chips = self.chips + amount

    def subtract_chips(self, amount):
        """ Remove chips from the players stack. """
        # NOTE: Separate function to hopefully help prevent errors.
        if amount < 0:
            raise RounderException("Negative amount, use add_chips instead.")
        logger.debug("Subtracting chips from " + str(self.username) + ": " +
            str(amount))
        self.chips = self.chips - amount


