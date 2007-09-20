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

CHIPS = 1000

def create_players_list(size, chips):
    """
    Create a list of players of the given size.
    """
    l = []
    for i in range(size):
        l.append(Player(name='player' + str(i), seat=i, chips=Currency(chips)))
    return l

def create_table(num_players, dealer_index):
    limit = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
    table = Table(name="Test Table", limit=limit, seats=10)

    players = []
    for i in range(num_players):
        new_player = Player(name='player' + str(i), chips=Currency(CHIPS))
        table.seat_player(new_player, i)
        players.append(new_player)

    return (limit, table, players)

