#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006-2008 James Bowes <jbowes@dangerouslyinc.com>
#   Copyright (c) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
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

""" The Rounder Pot Module (the kind you have at a poker table) """

from logging import getLogger
from collections import defaultdict
logger = getLogger("rounder.pot")
from currency import Currency

class Pot:
    """ 
    A single pot, used for both main and side pots. 
    
    NOTE: Do not try to smoke!
    """
    def __init__(self, players):
        # Players eligible for this pot:
        self.players = players[:]
        self.amount = Currency(0)

    def __add__(self, amount):
        self.amount += amount
        return self

    def is_player_eligible(self, player):
        """
        True if player is eligible to win this pot, False otherwise.
        """
        return player in self.players

    def debug(self):
        logger.debug("Pot: $%s" % self.amount)
        logger.debug("Players: " + str(self.players))



class PotManager:
    def __init__(self):
        self.pots = []
        self.createNew = True

    def __add_players_to_pot(self, players, amount):
        if self.createNew == True:
            self.createNew = False
            self.pots.insert(0, Pot(players))

        self.pots[0] += amount * len(players)

    # Called only once per betting round
    def add(self, player_amounts):
        amounts = player_amounts.keys()
        amounts.sort()
        players = []
        map(players.extend, player_amounts.values())
        already_in = 0
        for amount in amounts:
            self.__add_players_to_pot(players, amount - already_in)
            already_in = amount
            for player in player_amounts[amount]:
                if player.allin:
                    self.createNew = True
                players.remove(player)

    def fold(self, player):
        """ Make this player no longer eligible for any of the pots. """
        for pot in self.pots:
            if player in pot.players:
                pot.players.remove(player)

    def total_value(self):
        return reduce(lambda x, y: x + y.amount, self.pots, 0)
