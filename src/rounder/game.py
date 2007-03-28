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


GAME_ID_COUNTER = 1

class Game:

    """ Parent class of all poker games. """

    def __init__(self):
        # Every hand played needs a unique ID:
        self.id = ++GAME_ID_COUNTER

    def start(self):
        """ Begin the hand. """
        pass

    def perform(self, user, action):
        """ 
        Receive and incoming action request from a player. 
        This callback may be called directly in unit tests, but normally
        would originate from a call to the server and trickle down.
        """
        pass
        


class TexasHoldemGame(Game):

    """ Texas Hold'em, the king of all poker games. """
    # TODO: map pending player actions

    def __init__(self, limit, players, dealer):
        Game.__init__(self)
        self.limit = limit
        self.players = players
        self.dealer = dealer

    def start(self):
        pass

    def post_blinds(self):
        blind_seats = self.__calculate_blind_seats()
        post_sb = PostBlind(self, blind_seats[0], self.limit.small_blind)
        post_bb = PostBlind(self, blind_seats[1], self.limit.big_blind)
        blind_seats[0].prompt([post_sb])
        blind_seats[1].prompt([post_bb])

    def __calculate_blind_seats(self):
        return (self.players[self.dealer + 1], self.players[self.dealer + 2])

    def perform(self, action):
        logger.info("ACTION: " + str(action))
        
        # TODO: Clean this up:
        if isinstance(action, PostBlind):
            action.player.chips = action.player.chips - action.amount

