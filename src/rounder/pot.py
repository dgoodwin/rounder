#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2007 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006-2007 James Bowes <jbowes@dangerouslyinc.com>
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
logger = getLogger("rounder.pot")

from rounder.currency import Currency

class Pot:
    """
    Representation of a poker pot.

    Normally a single pot is in play for any given hand. If a player goes
    all in and betting continues, a new pot must be created.
    """

    def __init__(self, players):
        self.players = players
        self.amount = Currency(0.00)

        # A map of player to amount contributed to the pot, can be used both
        # as a definitive list of all players who were present when this game
        # started (as they're removed from the list when sitting out), as well
        # as a record of how much to refund to each player in the event this
        # game is aborted.
        self.in_pot = {}
        for p in self.players:
            self.in_pot[p] = Currency(0.00)

        self.bet_to_match= Currency(0.00)
        self.in_pot_this_betting_round = {}
            
    def refund_all(self):
        """ Refund each player's contribution. """
        for p in self.players:
            p.clear_pending_actions()
            p.add_chips(self.in_pot[p])
            self.amount = self.amount - self.in_pot[p]
            self.in_pot[p] = Currency(0.00)

    def reset_betting_round(self):
        """
        Resets any members tracking data for the current round of betting. Can
        be used both when starting a new game or moving on to the next round
        of betting within an existing game.
        """
        self.bet_to_match = Currency(0.00)
        self.in_pot_this_betting_round = {}

    def add(self, player, amount):
        """ Add funds from player to the pot. """
        player.subtract_chips(amount)
        self.amount = self.amount + amount
        self.in_pot[player] = self.in_pot[player] + amount

        if not self.in_pot_this_betting_round.has_key(player):
            self.in_pot_this_betting_round[player] = amount
        else:
            self.in_pot_this_betting_round[player] = \
                self.in_pot_this_betting_round[player] + amount

    def split(self, winners):
        """ 
        Split the pot up as evenly as possible amongst the list of winners. 

        Potential remaining cent is given to first player in the list.
        """
        logger.info("Splitting pot: " + str(self.amount))
        per_player = self.amount / len(winners)
        remainder = self.amount - (per_player * len(winners))
        logger.debug("remainder = " + str(remainder))
        
        for p in winners:
            winnings = per_player + remainder
            remainder = 0 # only add for the first player in the list
            p.add_chips(winnings)
            logger.info("   %s won %s" % (p.name, winnings))

