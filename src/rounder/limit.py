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

""" The Rounder Limit Module """

from logging import getLogger
logger = getLogger("rounder.limit")

from rounder.action import Call, Raise, Fold
from rounder.currency import Currency

class Limit:

    """ Parent class of all poker limits. """

    def __init__(self):
        pass

    def create_actions(self, player, in_pot, current_bet, bet_level):
        """ 
        Create the appropriate actions for this limit, the given player,
        and the current bet.

        in_pot is a Currency representing the amount the player has already
        contributed to the pot on this round of betting.

        bet_level is an integer representing a scale the limit can use when
        the structured bet changes throughout the hand.

        i.e. in limit holdem, a bet_level = 1 indicates the small bet is in
        effect (preflop, flop), and 2 indicates the big bet (turn, river)
        Other games may make use of this value.
        """
        pass



class FixedLimit(Limit):

    """ Representation of a fixed limit poker game. """

    def __init__(self, small_bet, big_bet, small_blind=None, big_blind=None):
        Limit.__init__(self)
        self.small_bet = small_bet
        self.big_bet = big_bet

        if small_blind is None:
            self.small_blind = self.small_bet / 2
        else:
            self.small_blind = small_blind

        if big_blind is None:
            self.big_blind = self.small_bet
        else:
            self.big_blind = big_blind

    def __repr__(self):
        return "$" + str(self.small_bet) + "/" + str(self.big_bet) + " limit"

    def create_actions(self, player, in_pot, current_bet, bet_level):
        logger.debug("creating actions")
        logger.debug("   player: %s" % player)
        logger.debug("   in_pot: %s" % in_pot)
        logger.debug("   current_bet: %s" % current_bet)
        logger.debug("   bet_level: %s" % bet_level)

        actions = []

        if in_pot is None:
            in_pot = Currency(0)

        call_amount = current_bet - in_pot
        if call_amount >= player.chips:
            call_amount = player.chips 
        else:
            raise_amount = self.big_bet
            if bet_level == 1:
                raise_amount = self.small_bet
            if raise_amount + current_bet > player.chips:
                raise_amount = player.chips - current_bet # all-in!
            actions.append(Raise(raise_amount, raise_amount))

        actions.append(Call(call_amount))

        actions.append(Fold())
        return actions

