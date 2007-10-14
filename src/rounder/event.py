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

Events should define a repr method which can be used for logging purposes.
It should not include the table name or ID as this will be a prefix when
the actual logging or display takes place.

Likewise the events do not need an actual reference to the table as this is
handled by the networking code.
"""


from rounder.dto import TableState

class Event:

    """ 
    Parent Event class. Events represent anything happening at a table that
    players need to be notified of.
    """

    def __init__(self, table):
        self.table_state = TableState(table)



class PlayerJoinedGame(Event):

    """ 
    Player joined the game.
    """

    def __init__(self, table, player_name, seat_num):
        Event.__init__(self, table)
        self.player_name = player_name
        self.seat_num = seat_num

    def __repr__(self):
        return "PlayerJoinedGame: %s took seat %s" % (self.player_name, 
            self.seat_num)



class PlayerSatOut(Event):

    """ 
    Player sat out. (but did not leave the table)
    """

    def __init__(self, table, player_name):
        Event.__init__(self, table)
        self.player_name = player_name

    def __repr__(self):
        return "PlayerSatOut: %s" % (self.player_name)



class NewHandStarted(Event):

    """
    Signals that a new hand is beginning.
    """

    def __init__(self, table):

        Event.__init__(self, table)



class PlayerPostedBlind(Event):

    """
    A player has agreed to post the blind.

    While players agree to post blinds before a hand is actually underway,
    this event is only sent when the hand begins and the blinds actually 
    enter the pot.
    """

    def __init__(self, table, player_name, amount):
        Event.__init__(self, table)
        self.player_name = player_name
        self.amount = amount



class HoleCardsDealt(Event):

    """
    Hole cards have been dealt to the player receiving the event. 
    (Player clients recieve no notification about hole cards being
    dealt to other players.)
    """

    def __init__(self, table, cards):

        Event.__init__(self, table)
        self.cards = cards



class CommunityCardsDealt(Event):

    """
    One or more community cards have been dealt.
    """

    def __init__(self, table, cards):

        Event.__init__(self, table)
        self.cards = cards



ALL_EVENTS = [
    Event, 
    PlayerJoinedGame,
    PlayerSatOut,
    NewHandStarted,
    PlayerPostedBlind,
    HoleCardsDealt,
    CommunityCardsDealt,
]

