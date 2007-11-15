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

class SidePot:
    """ A single pot, used for both main and side pots. """
    def __init__(self, players):
        # Players eligible for this pot:
        self.players = players
        self.amount = Currency(0.00)

class Pot:
    """
    Representation of a poker pot.

    Normally a single pot is in play for any given hand. If a player goes
    all in and betting continues, a new pot must be created.
    """

    def __init__(self, players):
        self.players = players

        # List of all pots, intially just 1 but more to come if players
        # start going all-in:
        self.pots = [SidePot(self.players)]

        # A map of player to amount contributed to the pot, can be used both
        # as a definitive list of all players who were present when this game
        # started (as they're removed from the list when sitting out), as well
        # as a record of how much to refund to each player in the event this
        # game is aborted.
        self.__in_pot = {}
        for p in self.players:
            self.__in_pot[p] = Currency(0.00)

        self.bet_to_match= Currency(0.00)
        self.__in_pot_this_betting_round = {}

    def bet_this_hand(self, player):
        return self.__in_pot[player]

    def bet_this_round(self, player):
        """ 
        Returns players total bets this round.
        """
        # TODO: Make multi-pot aware:
        if self.__in_pot_this_betting_round.has_key(player):
            return self.__in_pot_this_betting_round[player]
        return Currency(0.00)

    def has_bet_this_round(self, player):
        """ 
        Return True if player has contributed to this round of betting. 
        """
        return self.__in_pot_this_betting_round.has_key(player)

    def amount_to_match(self, player):
        """ Returns the amount this player must match to call the action. """
        bet_to_match = self.bet_to_match
        if self.__in_pot_this_betting_round.has_key(player):
            bet_to_match -= self.__in_pot_this_betting_round[player]
        return bet_to_match

    def total_value(self):
        """ Returns the total value of ALL pots. """
        total = Currency(0.00)
        for pot in self.pots:
            total += pot.amount
        return total
            
    def refund_all(self):
        """ Refund each player's contribution. """
        for pot in self.pots:
            for player in pot.players:
                player.clear_pending_actions()
                player.add_chips(self.__in_pot[player])
                pot.amount = pot.amount - self.__in_pot[player]
                self.__in_pot[player] = Currency(0.00)

    def reset_betting_round(self):
        """
        Resets any members tracking data for the current round of betting. Can
        be used both when starting a new game or moving on to the next round
        of betting within an existing game.
        """
        self.bet_to_match = Currency(0.00)
        self.__in_pot_this_betting_round = {}

    def add(self, player, amount):
        """ Add funds from player to the pot. """
        player.subtract_chips(amount)
        self.pots[0].amount = self.pots[0].amount + amount
        self.__in_pot[player] = self.__in_pot[player] + amount

        if not self.__in_pot_this_betting_round.has_key(player):
            self.__in_pot_this_betting_round[player] = amount
        else:
            self.__in_pot_this_betting_round[player] = \
                self.__in_pot_this_betting_round[player] + amount

    def split(self, winners):
        """ 
        Split the pot up as evenly as possible amongst the list of winners. 

        Potential remaining cent is given to first player in the list.
        """
        logger.info("Splitting pot: " + str(self.pots[0].amount))
        per_player = self.pots[0].amount / len(winners)
        remainder = self.pots[0].amount - (per_player * len(winners))
        logger.debug("remainder = " + str(remainder))
        
        for p in winners:
            winnings = per_player + remainder
            remainder = 0 # only add for the first player in the list
            p.add_chips(winnings)
            logger.info("   %s won %s" % (p.name, winnings))

