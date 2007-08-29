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
The Rounder Events Module 

Events are read-only data transfer objects used to pass to clients whenever
something happens that they need to be notified of. The objects do nothing,
just contain data.

Clients generally must type check incoming events to determine how to extract
the data and what to do with it.
"""

class Event:

    """ 
    Parent Event class. Events represent anything happening at a table that
    players need to be notified of.
    """

    def __init__(self):
        pass



class PlayerJoinedGame(Event):

    """ 
    Player joined the game.
    """

    def __init__(self, player_name, seat_num):
        Event.__init__(self)
        self.player_name = player_name
        self.seat_num = seat_num

    def __repr__(self):
        return "PlayerJoinedGame: %s took seat %s" % (self.player_name, 
            self.seat_num)



ALL_EVENTS = [
    Event, 
    PlayerJoinedGame,
]

