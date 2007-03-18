#!/usr/bin/env python

import types

from rounder.core import RounderException

class Suit:
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
allSuits = [SPADE, DIAMOND, CLUB, HEART]
ranksAcsending = range(2, 15)
ranksDescending = range(14, 1, -1)

# Maps card values to display values:
rankToString = {
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
stringToRank = {
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

stringToSuit = {
    's': SPADE,
    'd': DIAMOND,
    'c': CLUB,
    'h': HEART
}

def getRankDisplay(intRank):
    return rankToString[intRank]

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
        self.__createCard(rank,suit)

    def __createCard(self, rank, suit):
        if type(rank) == types.IntType and rank >= 2 and rank <= 14:
            self.rank = rank
        elif stringToRank.has_key(str(rank)):
            self.rank = stringToRank.get(str(rank))
        else:
            raise RounderException("Bad card rank: " + str(rank))

        if isinstance(suit, Suit):
            self.suit = suit
        elif stringToSuit.has_key(str(suit)):
            self.suit = stringToSuit.get(str(suit))
        else:
            raise RounderException("Bad card suit: " + str(suit))

    def __str__(self):
        return "%s%s" % (self.getRankDisplay(), self.getSuitDisplay())

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

    def getRankDisplay(self):
        return getRankDisplay(self.rank)

    def getSuitDisplay(self):
        return self.suit.display

    def getLongSuitDisplay(self):
        return self.suit.longDisplay
