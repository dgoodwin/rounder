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

""" The Rounder Player Module """

from logging import getLogger
logger = getLogger("rounder.player")

from rounder.core import NotImplementedException, RounderException
from rounder.action import PostBlind

class Player:

    """ 
    Player at a poker table. Note one account could be playing at 
    multiple tables concurrently, in which case one Player would be
    created for each.
    """

    def __init__(self, name, table=None, seat=None, chips=0):
        self.name = name
        self.chips = chips
        self.table = table
        self.seat = seat
        self.cards = []
        self.final_hand = None
        self.final_hand_rank = None
        self.sitting_out = False
        self.folded = False
        self.pending_actions = []

    def reset(self):
        """ Reset player state specific to a hand. """
        self.cards = []
        self.final_hand = None
        self.final_hand_rank = None
        self.folded = False
        self.pending_actions = []
        
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
            (self.name, self.seat, self.chips)

    def clear_pending_actions(self):
        """ Clear any actions pending for this player. """
        logger.debug("Clearing pending actions: " + str(self.pending_actions))
        self.pending_actions = []

    def sit_out(self):
        """ Sit player out of the game. """
        self.sitting_out = True

    def sit_in(self):
        """ Sit player back in the game. """
        self.sitting_out = False

    def add_chips(self, amount):
        """ Add chips to the players stack. """
        if amount < 0:
            raise RounderException("Negative amount, use subtract_chips instead.")
        logger.debug("Adding chips to " + str(self.name) + ": " + str(amount))
        self.chips = self.chips + amount

    def subtract_chips(self, amount):
        """ Remove chips from the players stack. """
        # NOTE: Separate function to hopefully help prevent errors.
        if amount < 0:
            raise RounderException("Negative amount, use add_chips instead.")
        logger.debug("Subtracting chips from " + str(self.name) + ": " + 
            str(amount))
        self.chips = self.chips - amount


