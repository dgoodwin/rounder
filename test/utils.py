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

""" Rounder Test Utilities """

from rounder.table import Table
from rounder.currency import Currency
from rounder.player import Player
from rounder.limit import FixedLimit
from rounder.card import Card

CHIPS = 1000


def create_players_list(size, chips):
    """
    Create a list of players of the given size.
    """
    l = []
    for i in range(size):
        l.append(Player(username='player' + str(i),
                        seat=i,
                        chips=Currency(chips)))
    return l


def create_players(chip_counts):
    """
    Create a list of players with chip counts corresponding to the
    incoming list.
    """
    l = []
    i = 0
    for c in chip_counts:
        l.append(Player(username='player' + str(i), seat=i, chips=Currency(c)))
        i = i + 1
    return l


def create_table(chip_counts, dealer_index):
    limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
    table = Table(name="Test Table", limit=limit, seats=10)

    players = []
    i = 0
    for chip_count in chip_counts:
        new_player = Player(username='player' + str(i),
                            chips=Currency(chip_count))
        table.seat_player(new_player, i)
        players.append(new_player)
        i = i + 1

    return (limit, table, players)


def create_cards_from_list(value_list):
    return [Card(value) for value in value_list]


def reorder_deck(deck, card_list):
    """Pull the list of values to the front of the deck

    It should be noted that this will reorder the deck and therefore
    should not be run after any cards are handed out to players.

    """
    count = 0
    for card in card_list:
        index = deck.cards.index(card)

        # Take the actual card instead of the list because they could just
        # compare the same.
        card = deck.cards[index]
        deck.cards[index] = deck.cards[count]
        deck.cards[count] = card
        count += 1


