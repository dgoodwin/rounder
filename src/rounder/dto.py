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

""" 
Rounder Data Transfer Objects

Various objects used to safely transmit game state or activity to clients. 
In cases where an engine object is considered safe to transmit to a client,
a DTO should still be created as child class of the engine object. Even if
initially empty it provides a hook for us to change the DTO should the
engine object later grow to contain sensitive information.
"""

from rounder.currency import Currency

class TableState:
    """ 
    Representation of a table fit for sending to a table's observers. 
    Must be careful not to expose any engine internals, this WILL be
    transferred over the wire.
    """

    def __init__(self, table):
        self.id = table.id
        self.name = table.name
        self.limit = table.limit
        self.hand_underway = (table.gsm.current != None)
        self.community_cards = []
        self.pots = []
        self.round_bets = Currency(0.00)
        if table.game != None:
            self.community_cards = table.game.community_cards
            for pot in table.game.pot_mgr.pots:
                self.pots.append(PotState(pot))

            # Pots only receive funds after the round of betting has completed,
            # but clients are more than a little interested in seeing the
            # amount of money bet in the current round as well. Include this
            # info and let the client figure out how they want to render it.
            # (as it's not really part of any pot yet, nor do we know which it
            # will go to)
            for p in table.game.players:
                self.round_bets = self.round_bets + p.current_bet

        # for now represent seated players as a list of tuples, player name
        # and stack size:
        self.seats = []
        for seat_num in range(table.seats.get_size()):
            p = table.seats.get_player(seat_num)
            if p is None:
                self.seats.append(None)
            else:
                self.seats.append(PlayerState(p))

    def print_state(self):
        """ Print the table state. """
        print "Table state for table: %s" % self.name
        print "   hand underway: %s" % self.hand_underway
        i = 0
        print "   seats:"
        for s in self.seats:
            print "     %s - %s" % (i, s)
            i = i + 1



class TableListing:
    """
    Minimal representation of a table for use in the server window's table 
    list.

    Contains only necessary information such as table ID, name, limit, and
    the current number of players. Differs from the TableState object which
    contains enough information to update the table on an observers screen.
    """

    def __init__(self, table):
        self.id = table.id
        self.name = table.name
        self.limit = table.limit
        self.player_count = len(table.seats.seated_players)

    def __str__(self):
        return "%s - %s - %s players" % (self.name,
            self.limit, self.player_count)



class PlayerState:
    """ 
    Representation of a Player safe for transmitting over the wire.
    """

    def __init__(self, player):
        self.username = player.username
        self.chips = player.chips
        self.seat = player.seat
        self.sitting_out = player.sitting_out
        self.folded = player.folded

        self.num_cards = len(player.cards)

    def __str__(self):
        return "%s - %s" % (self.username, self.chips)



class PotState:
    """
    Representaton of a Pot safe for transmitting over the wire.

    The Pot class itself is dangerously close to being safe to transmit as it,
    but wrapping it here just incase the references to players will
    pose a problem, or inappropriate information is added in the future.
    """

    def __init__(self, pot):
        self.amount = pot.amount
        self.is_main_pot = pot.is_main_pot

    def __repr__(self):
        return "Pot: $%s" % self.amount



class PotWinner:
    """
    Winner of a pot.
    """

    def __init__(self, username, amount):
        self.username = username
        self.amount = amount

    def __repr__(self):
        return "PotWinner: %s won $%s" % (self.username, self.amount)

