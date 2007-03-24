#   Rounder - Poker for the Gnome Desktop
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

""" Module for processing and ranking hands. """

from logging import getLogger
logger = getLogger("rounder.deck")

import rounder.card
from rounder.core import RounderException
from rounder.core import array_to_string

class HandRank:
    """
    Base class for the hand ranks.
    """
    def __init__(self, id, displayName):
        self.id = id
        self.displayName = displayName

    def eval(self, cards):
        """
        Returns a tuple of a boolean representing weather or not the supplied
        cards qualify for this type of hand, and the final 5 cards composing
        the best possible hand of this rank.
        """
        raise NotImplementedError

class StraightFlush(HandRank):
    def __init__(self):
        HandRank.__init__(self, 9, "straight flush")

    def eval(self, cards):
        if len(cards.flushSuits) > 0:
            bestStrFlush = []
            for s in cards.flushSuits:
                strFlushCards = check_for_straight(filter_suit(
                    cards.sortedCards, s))
                if len(strFlushCards) == 5:
                    if len(bestStrFlush) != 5 or \
                        strFlushCards[0].rank > bestStrFlush[0].rank:
                        bestStrFlush = strFlushCards

            if len(bestStrFlush) == 5:
                return (True, bestStrFlush)
        return (False, [])

class FourOfAKind(HandRank):
    def __init__(self):
        HandRank.__init__(self, 8, "four of a kind")

    def eval(self, cards):
        finalHand = []
        quadsRank = -1
        for rank in rounder.card.RANKS_DESCENDING:
            if cards.rankCount[rank] == 4: 
                finalHand.extend(filter_rank(cards.sortedCards, rank))
                return (True, finalHand)
        return (False, [])

class FullHouse(HandRank):
    def __init__(self):
        HandRank.__init__(self, 7, "full house")

    def eval(self, cards):
        finalHand = []
        tripsRank = -1
        pairRank = -1
        for rank in rounder.card.RANKS_DESCENDING:
            if cards.rankCount[rank] == 3:
                if tripsRank == -1:
                    tripsRank = rank
                elif pairRank == -1:
                    pairRank = rank
            elif cards.rankCount[rank] == 2:
                if pairRank == -1:
                    pairRank = rank
        if (tripsRank != -1) and (pairRank != -1):
            finalHand.extend(filter_rank(cards.sortedCards, tripsRank))
            finalHand.extend(filter_rank(cards.sortedCards, pairRank, 2))
            return (True, finalHand)
        return (False, [])

class Flush(HandRank):
    def __init__(self):
        HandRank.__init__(self, 6, "flush")

    def eval(self, cards):
        if len(cards.flushSuits) > 0:
            # TODO: Problems here with flushes of the same high card but a
            # lower following card. ie. Player A has KJT52 of diamonds,
            # player B somehow has two flushes at his disposal, one where
            # he can make KT784 and a second one where he can make KQ784.
            # The first flush would register as it has the highest available
            # card. I know of no poker games where this situation is possible.
            bestFlush = []
            for s in cards.flushSuits:
                flushCards = filter_suit(cards.sortedCards, s)
                if len(bestFlush) != 5 or \
                    flushCards[0].rank > bestFlush[0].rank:
                    bestFlush = flushCards
            return (True, bestFlush)

        return (False, [])

class Straight(HandRank):
    def __init__(self):
        HandRank.__init__(self, 5, "straight")

    def eval(self, cards):
        straightCards = check_for_straight(cards.sortedCards)
        if len(straightCards) == 5:
            return (True, straightCards)

        return (False, [])

class ThreeOfAKind(HandRank):
    def __init__(self):
        HandRank.__init__(self, 4, "three of a kind")

    def eval(self, cards):
        tripsRank = -1
        finalHand = []
        for rank in rounder.card.RANKS_DESCENDING:
            if cards.rankCount[rank] == 3:
                tripsRank = rank
                break
        if tripsRank != -1:
            finalHand.extend(filter_rank(cards.sortedCards, tripsRank))
            return (True, finalHand)

        return (False, [])

class TwoPair(HandRank):
    def __init__(self):
        HandRank.__init__(self, 3, "two pair")

    def eval(self, cards):
        finalHand = []
        pairRanks = []
        for rank in rounder.card.RANKS_DESCENDING:
            if cards.rankCount[rank] == 2:
                pairRanks.append(rank)
                if len(pairRanks) == 2:
                    break

        if len(pairRanks) >= 2:
            finalHand.extend(filter_rank(cards.sortedCards, pairRanks[0]))
            finalHand.extend(filter_rank(cards.sortedCards, pairRanks[1]))
            return (True, finalHand)

        return (False, [])

class OnePair(HandRank):
    def __init__(self):
        HandRank.__init__(self, 2, "one pair")

    def eval(self, cards):
        for rank in rounder.card.RANKS_DESCENDING:
            if cards.rankCount[rank] == 2:
                finalHand = []
                finalHand.extend(filter_rank(cards.sortedCards, rank))
                return (True, finalHand)
        
        return (False, [])

class HighCard(HandRank):
    def __init__(self):
        HandRank.__init__(self, 1, "high card")

    def eval(self, cards):
        return (True, [])

HIGHCARD = HighCard()
ONEPAIR = OnePair()
TWOPAIR = TwoPair()
THREEOFAKIND = ThreeOfAKind()
STRAIGHT = Straight()
FLUSH = Flush()
FULLHOUSE = FullHouse()
FOUROFAKIND = FourOfAKind()
STRAIGHTFLUSH = StraightFlush()

handRanks = [STRAIGHTFLUSH, FOUROFAKIND, FULLHOUSE, FLUSH, STRAIGHT,
    THREEOFAKIND, TWOPAIR, ONEPAIR, HIGHCARD]

class AvailableCards:
    """
    Carries computational information about the available cards so we can hand
    it around to the various hand rank evaluators without recalculating every
    time.
    """
    def __init__(self, cards):
        self.cards = cards

        # Copy cards and sort, leave the originals intact:
        self.sortedCards = []
        self.sortedCards.extend(cards)
        self.sortedCards.sort()
        self.suitCount = {
            rounder.card.SPADE: 0, 
            rounder.card.DIAMOND: 0, 
            rounder.card.CLUB: 0, 
            rounder.card.HEART: 0
        }
        self.rankCount = {
            2: 0, 
            3: 0, 
            4: 0, 
            5: 0, 
            6: 0, 
            7: 0, 
            8: 0, 
            9: 0, 
            10: 0, 
            11: 0, 
            12: 0, 
            13: 0,
            14: 0
        }

        for c in self.sortedCards:
            self.suitCount[c.suit] = self.suitCount[c.suit] + 1
            self.rankCount[c.rank] = self.rankCount[c.rank] + 1

        self.flushSuits = []
        for i in rounder.card.ALL_SUITS:
            if self.suitCount[i] >= 5:
                self.flushSuits.append(i)
                self.flushedCards = filter_suit(self.sortedCards, i)

class HandProcessor:

    """ 
    Base hand processor class, extended as necessary by poker variants
    that require a non-standard interpretation of the hands.
    """

    pass

class DefaultHandProcessor:
    """
    Evaluates hands according to the standard poker rules and hand rankings.

    Contain no state and can safely be reused across any objects
    requiring their functionality.
    """

    def evaluate(self, cards):
        """
        Returns the best possible hand made from the supplied cards. As this is a
        final hand, atleast 5 cards must be supplied and exactly 5 returned.
        """
        if len(cards) < 5:
            raise NotEnoughCardsException("5 cards required to evaluate" \
                + " a hand, only " + str(len(cards)) + " present.")
        evalResults = self.__evaluate(cards)
        finalCards = evalResults[1]
        if len(finalCards) > 5:
            raise RounderException("Too many cards returned during evaluation.")
        elif len(finalCards) < 5:
            finalCards.extend(get_kickers(5 - len(finalCards), cards,
                finalCards))
        return (evalResults[0], finalCards)

    def __evaluate(self, cards):
        """
        Returns the currently best possible hand, and the cards that compose it.
        This function can be called with less than 5 cards, and will naturally
        only return the cards that are required to make the best hand thus far.
        """

        availableCards = AvailableCards(cards)

        for rank in handRanks:
            evalResults = rank.eval(availableCards)
            if evalResults[0]:
                logger.debug("Evaluated " + array_to_string(cards) + " to " + \
                    rank.displayName)
                return (rank, evalResults[1])

        # If we get to this point, something is very very wrong.
        raise RounderException("Unable to determine hand rank for: " + \
            array_to_string(cards))

class NotEnoughCardsException(RounderException):
    """
    Thrown when we try to evaluate a hand containing less than 5 cards.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def check_for_straight(sortedCards):
    """
    Check all possible combinations of the given cards for any occurance of a
    straight. Suits are not considered, duplicate ranks get removed with the
    first card of a given rank being the one considered in the straight. If
    you're interested in checking for straight flushes, you pass in only
    cards of the suit in question.

    sortedCards must be sorted!!!
    """
    uniqueRankedCards = remove_duplicate_ranks(sortedCards)
    
    if (len(uniqueRankedCards) < 5):
        return []
    foundStraight = False
    lowIndex = 0
    highIndex = 5
    while highIndex <= len(uniqueRankedCards):
        if is_straight(uniqueRankedCards[lowIndex:highIndex]):
            return uniqueRankedCards[lowIndex:highIndex]
        lowIndex = lowIndex + 1
        highIndex = highIndex + 1

    # Need to reposition aces at the bottom to check for the wheel:
    if rounder.card.RANK_TO_STRING[uniqueRankedCards[0].rank] == 'A' and \
        rounder.card.RANK_TO_STRING[uniqueRankedCards[-1].rank] == '2':
        potentialWheel = uniqueRankedCards[-4:]
        potentialWheel.append(uniqueRankedCards[0])
        if is_straight(potentialWheel):
            return potentialWheel

    # Return an empty list if no straight was found:
    return []

def is_straight(fiveCards):
    """ Check if the 5 provided cards constitute a straight. """
    if len(fiveCards) != 5:
        raise RounderException("Checking for straight on less than " +
            "five cards.")
    i = 1
    while i < 5:
        if fiveCards[i].rank != (fiveCards[i - 1].rank - 1):
            if fiveCards[i].rank == 14 and fiveCards[i - 1].rank == 2:
                pass
            else:
                return False
        i = i + 1
    return True

def filter_suit(cards, suit):
    """
    Returns a list of all the cards found in the supplied list that match
    the suit requested.
    """
    filteredCards = []
    for c in cards:
        if c.suit == suit:
            filteredCards.append(c)
    return filteredCards

def filter_rank(cards, rank, max=-1):
    """
    Returns a list of all cards found in the supplied list that match the
    rank requested.
    """
    filteredCards = []
    for c in cards:
        if c.rank == rank:
            if max == -1 or len(filteredCards) < max:
                filteredCards.append(c)
    return filteredCards

def get_kickers(howMany, cards, cardsToExclude=[]):
    """
    Returns a list of kickers, as many as we need, excluding the ranks we
    don't want. List of cards absolutely must be sorted.
    """
    kickers = []

    # Remove duplicate cards, sort the remaining cards by rank:
    sortedCards = []
    sortedCards.extend(cards)
    for c in cardsToExclude:
        sortedCards.remove(c)
    sortedCards.sort()

    for c in sortedCards:
        kickers.append(c)
        if len(kickers) == howMany:
            return kickers
    raise RounderException("Unable to find %s kickers!")

def remove_duplicate_ranks(cards):
    """
    Remove duplicate ranks, the first card of a rank is the one that remains.
    i.e. Suits don't matter to us.
    """
    returnCards = []
    for i in range(len(cards)):
        if i == 0 or cards[i].rank != cards[i - 1].rank:
            returnCards.append(cards[i])
    return returnCards

