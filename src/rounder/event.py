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



class PlayerJoinedTable(Event):

    """
    Player sat down at the table.
    """

    def __init__(self, table, username, seat_num):
        Event.__init__(self, table)
        self.username = username
        self.seat_num = seat_num

    def __repr__(self):
        return "PlayerJoinedTable: %s took seat %s" % (self.username,
            self.seat_num)



class PlayerLeftTable(Event):

    """
    Player left the table.
    """

    def __init__(self, table, username, seat_num):
        Event.__init__(self, table)
        self.username = username
        self.seat_num = seat_num

    def __repr__(self):
        return "PlayerLeftTable: %s left seat %s" % (self.username,
            self.seat_num)



class PlayerSatOut(Event):

    """
    Player sat out. (but did not leave the table)
    """

    def __init__(self, table, username):
        Event.__init__(self, table)
        self.username = username

    def __repr__(self):
        return "PlayerSatOut: %s" % (self.username)



class PlayerPrompted(Event):

    """
    Player has been prompted with actions.
    """

    def __init__(self, table, username):

        Event.__init__(self, table)
        self.username = username

    def __repr__(self):
        return "PlayerPrompted: %s" % self.username



class HandCancelled(Event):

    """
    Signals that a hand was cancelled. Usually happens when we attempt to
    start a game but are unable to find players willing to post the blinds.
    """

    def __init__(self, table):

        Event.__init__(self, table)



class NewHandStarted(Event):

    """
    Signals that a new hand is beginning.
    """

    def __init__(self, table, players):

        Event.__init__(self, table)
        self.seats_dealt_in = []
        for p in players:
            self.seats_dealt_in.append(p.seat)



class PlayerPostedBlind(Event):

    """
    A player has agreed to post the blind.

    While players agree to post blinds before a hand is actually underway,
    this event is only sent when the hand begins and the blinds actually
    enter the pot.
    """

    def __init__(self, table, username, amount):
        Event.__init__(self, table)
        self.username = username
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



class PlayerCalled(Event):

    """
    Player called the current bet.

    Amount is the amount they called, excluding anything they had
    previously committed to the pot on previous action.
    """

    def __init__(self, table, username, amount):

        Event.__init__(self, table)
        self.username = username
        self.amount = amount



class PlayerRaised(Event):

    """
    Player raised the current bet.

    Amount is the amount raised over the existing bet.
    """

    def __init__(self, table, username, amount):

        Event.__init__(self, table)
        self.username = username
        self.amount = amount



class PlayerFolded(Event):

    """
    Player folded.
    """

    def __init__(self, table, username):

        Event.__init__(self, table)
        self.username = username

    def __repr__(self):
        return "PlayerFolded: %s" % self.username


class GameEnding(Event):
    """
    Game is ending.

    Clients should not interpret this as the actual end of the game, but
    rather wait for incoming PlayerShowedCards events, and finally a 
    GameResults event with information about who won each pot.
    """
    
    def __init__(self, table):
        Event.__init__(self, table)



class GameOver(Event):
    """
    Game is over.

    Contains all the final results of the hand, who won with what hand
    and how much.
    """
    
    def __init__(self, table, results):
        Event.__init__(self, table)

        # A list of tuples, (PotState, [PotWinner, ...]):
        self.results = results



class PlayerShowedCards(Event):
    """
    Player shows their hole cards.

    Only used at the end of a hand. Currently sent out for all players left in
    the hand, but one day may be optional for users who aren't required to
    show first.
    """

    def __init__(self, table, username, cards):

        Event.__init__(self, table)
        self.username = username
        self.cards = cards

    def __repr__(self):
        return "PlayerShowedCards: %s - %s" % (self.username, self.cards)


# All events should be added to this list for automatic serialization:
ALL_EVENTS = [
    Event,
    PlayerJoinedTable,
    PlayerLeftTable,
    PlayerPrompted,
    PlayerSatOut,
    NewHandStarted,
    HandCancelled,
    PlayerPostedBlind,
    HoleCardsDealt,
    CommunityCardsDealt,
    PlayerCalled,
    PlayerRaised,
    PlayerFolded,
    GameEnding,
    PlayerShowedCards,
    GameOver,
]

