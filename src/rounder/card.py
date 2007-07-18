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

""" Rounder module containing functionality related to a playing card. """

import types

from rounder.core import RounderException

class Suit:
    
    """ Object representation of a card suit. """

    def __init__(self, uniqueInt, shortDisplay, longDisplay):
        self.uniqueInt = uniqueInt
        self.display = shortDisplay
        self.longDisplay = longDisplay

    def __str__(self):
        return self.display



SPADE = Suit(0, "s", "spade")
DIAMOND = Suit(1, "d", "diamond")
CLUB = Suit(2, "c", "club")
HEART = Suit(3, "h", "heart")

# Handy for iteration purposes:
ALL_SUITS = [SPADE, DIAMOND, CLUB, HEART]
RANKS_ASCENDING = range(2, 15)
RANKS_DESCENDING = range(14, 1, -1)

# Maps card values to display values:
RANK_TO_STRING = {
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'T',
    11: 'J',
    12: 'Q',
    13: 'K',
    14: 'A'
}
STRING_TO_RANK = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}

STRING_TO_SUIT = {
    's': SPADE,
    'd': DIAMOND,
    'c': CLUB,
    'h': HEART
}

def get_rank_display(intRank):
    return RANK_TO_STRING[intRank]

class Card:
    """ Standard playing card. """
    def __init__(self, rank, suit=None):
        """
        Create a standard playing card. Card can be created in a number
        of ways, the following are all valid:

           (14, 'c')
           ('A', 'c')
           ('A', Club)
           ('Ac')
        """
        if suit == None:
            rank = str(rank)
            if (len(rank) < 2):
                raise RounderException("Bad card: " + rank)
            suit = rank[-1:]
            rank = rank[:-1]
        self.__create_card(rank, suit)

    def __create_card(self, rank, suit):
        if type(rank) == types.IntType and rank >= 2 and rank <= 14:
            self.rank = rank
        elif STRING_TO_RANK.has_key(str(rank)):
            self.rank = STRING_TO_RANK.get(str(rank))
        else:
            raise RounderException("Bad card rank: " + str(rank))

        if isinstance(suit, Suit):
            self.suit = suit
        elif STRING_TO_SUIT.has_key(str(suit)):
            self.suit = STRING_TO_SUIT.get(str(suit))
        else:
            raise RounderException("Bad card suit: " + str(suit))

    def __str__(self):
        return "%s%s" % (self.get_rank_display(), self.get_suit_display())

    def __cmp__(self, other):
        if other.rank != self.rank:
            return cmp(other.rank, self.rank)
        else:
            if other.suit.uniqueInt == self.suit.uniqueInt:
                return 0
            # Maintain the order, but don't allow cards with the same rank to
            # be interpreted as the same card.
            else:
                return 1

    def get_rank_display(self):
        return get_rank_display(self.rank)

    def get_suit_display(self):
        return self.suit.display

    def get_long_suit_display(self):
        return self.suit.longDisplay
