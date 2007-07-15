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
"""

class TableState:

    """ 
    Representation of a table fit for sending to a table's observers. 
    Must be careful not to expose any engine internals, this WILL be
    transferred over the wire.
    """

    def __init__(self, table):
        self.id = table.name
        self.name = table.name

        # for now represent seated players as a list of tuples, player name
        # and stack size:
        self.seats = []
        for seat_num in range(table.seats.get_size()):
            p = table.seats.get_player(seat_num)
            if p is None:
                self.seats.append((None, None))
            else:
                self.seats.append((p.name, p.chips))




