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
    """ A single pot, used for both main and side pots. """
    def __init__(self, players):
        # Players eligible for this pot:
        self.players = players
        self.amount = Currency(0.00)
        self.bet_to_match = Currency(0.00)

        # A map of player to amount contributed to the pot, can be used both
        # as a definitive list of all players who were present when this game
        # started (as they're removed from the list when sitting out), as well
        # as a record of how much to refund to each player in the event this
        # game is aborted.
        self.hand_bets = {}
        for p in self.players:
            self.hand_bets[p] = Currency(0.00)

        self.round_bets = {}

    def get_amount_owing(self, player):
        """ 
        Return the amount this player must contribute to this pot. 
        If the player doesn't have the chips required to match, we return their
        chips instead.
        """
        owes = self.bet_to_match 
        if self.round_bets.has_key(player):
            owes = owes - self.round_bets[player]
        if owes >= player.chips:
            return player.chips
        else: 
            return owes

class PotManager:
    """
    Representation of a poker pot.

    Normally a single pot is in play for any given hand. If a player goes
    all in and betting continues, a new pot must be created.
    """

    def __init__(self, players):
        self.players = players

        # List of all pots, intially just 1 but more to come if players
        # start going all-in:
        self.pots = [Pot(self.players)]

        # Set to true when we need to be on the lookout for a raise:
        self.__new_side_pot_on_raise = False

    def __get_bet_to_match(self):    
        """ Getter for bet_to_match on all sub-pots. """
        total_bet_to_match = Currency(0.00)
        for pot in self.pots:
            total_bet_to_match += pot.bet_to_match
        return total_bet_to_match

    def __set_bet_to_match(self, val):
        """ Setter for bet_to_match on all sub-pots. """
        # TODO: Get smart here...
        self.pots[0].bet_to_match = val

    bet_to_match = property(__get_bet_to_match, __set_bet_to_match)

    def bet_this_hand(self, player):
        """ Return true if player has contributed to the pot this hand. """
        bets = Currency(0.00)
        for pot in self.pots:
            bets += pot.hand_bets[player]
        return bets


    def bet_this_round(self, player):
        """ 
        Returns players total bets this round.
        """
        bets = Currency(0.00)
        for pot in self.pots:
            if pot.round_bets.has_key(player):
                bets += pot.round_bets[player]
        return bets

    def has_bet_this_round(self, player):
        """ 
        Return True if player has contributed to this round of betting. 
        """
        for pot in self.pots:
            if pot.round_bets.has_key(player):
                return True
        return False

    def amount_to_match(self, player):
        """ Returns the amount this player must match to call the action. """
        bet_to_match = self.bet_to_match
        bet_to_match -= self.bet_this_round(player)
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
                refund_amnt = self.bet_this_round(player)
                player.add_chips(refund_amnt)
                pot.amount = pot.amount - refund_amnt
                pot.hand_bets[player] = Currency(0.00)

    def reset_betting_round(self):
        """
        Resets any members tracking data for the current round of betting. Can
        be used both when starting a new game or moving on to the next round
        of betting within an existing game.
        """
        for pot in self.pots:
            pot.bet_to_match = Currency(0.00)
            pot.round_bets = {}

    def raise_stakes(self, amount):
        """ Increase the bet to match. """
        logger.debug("Raised stakes to: %s" % amount)
        self.pots[0].bet_to_match = self.pots[0].bet_to_match + amount

    def add(self, player, amount):
        """ Add funds from player to the pot. """
        assert (amount <= player.chips)

        raised = False
        total_amnt = amount + self.bet_this_round(player)
        if total_amnt > self.pots[0].bet_to_match:
            logger.debug("Detected a raise, setting new bet to match: %s",
                amount + self.bet_this_round(player))
            raised = True

            if self.__new_side_pot_on_raise:
                logger.debug("Creating new side pot.")
                self.__new_side_pot_on_raise = False
                self.pots.append(Pot(self.players))
                # Calculate the bet_to_match for the new pot:
                new_bet_to_match = total_amnt - self.bet_to_match
                logger.debug("New pot bet to match: %s" % new_bet_to_match)
                self.pots[-1].bet_to_match = new_bet_to_match
            else:
                self.pots[-1].bet_to_match = total_amnt

        if amount == player.chips:
            if raised:
                logger.debug("%s has raised all-in" % player.name)
            else:
                logger.debug("%s has called all-in" % player.name)
            self.__new_side_pot_on_raise = True

        self.__delegate_amount_to_side_pots(player, amount)

    def __delegate_amount_to_side_pots(self, player, amount):
        """
        Split the incoming bet amount from the given player up amongst all
        available pots in the correct order.
        """

        logger.debug("__delegate_amount_to_side_pots")
        logger.debug("player = %s" % player.name)
        amount_copy = amount
        for pot in self.pots:
            owes_this_pot = pot.get_amount_owing(player)
            logger.debug("bet_to_match = %s" % pot.bet_to_match)
            logger.debug("%s owes_this_pot = %s" % (player.name, owes_this_pot))
            if not pot.round_bets.has_key(player):
                pot.round_bets[player] = owes_this_pot
            else:
                pot.round_bets[player] = \
                    pot.round_bets[player] + owes_this_pot

            if owes_this_pot > 0:
                amount_copy = amount_copy - owes_this_pot
                pot.amount = pot.amount + owes_this_pot
                pot.hand_bets[player] = pot.hand_bets[player] + owes_this_pot

                logger.debug("amount_copy = %s" % amount_copy)
                assert(amount_copy >= 0)
                if amount_copy == 0:
                    break

        player.subtract_chips(amount)

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

