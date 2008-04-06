#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2008 James Bowes <jbowes@dangerouslyinc.com>
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
PyPokerEval compatible hand ranker.
"""


import logging

log = logging.getLogger("rounder.evaluator")


class FullHand(object):

    def __init__(self, hand, table):
        fullhand = hand + table
        fullhand = list(fullhand)
        fullhand.sort()
        self.cards = fullhand

        self.ranks = {}
        for card in self.cards:
            rank = card[:-1]
            if not self.ranks.has_key(rank):
                self.ranks[rank] = []
            self.ranks[rank].append(card[-1])

        self.suits = {}
        for card in self.cards:
            suit = card[-1]
            if not self.suits.has_key(suit):
                self.suits[suit] = []
            self.suits[suit].append(card[:-1])

        self._relative_value = self._get_relative_value()

        printable_hand = "(%s) (%s)" % (', '.join(hand), ', '.join(table))
        log.debug("Hand '%s' has relative value 0x%.6X" % (printable_hand,
            self._relative_value))

    def is_royal(self):
       has_ace_high = False
       for card in self.cards:
           if card[:-1] == 'a':
               has_ace_high = True
               break
       return has_ace_high and self.is_straight_flush()

    def is_straight_flush(self):
        return self.is_flush() and self.is_straight()

    def is_quads(self):
        counts = [len(x) for x in self.ranks.values()]
        counts.sort()
        return counts[-1] == 4

    def is_full_house(self):
        counts = [len(x) for x in self.ranks.values()]
        counts.sort()

        return counts in [[1, 1, 2, 3], [2, 2, 3], [1, 3, 3]]

    def is_flush(self):
        counts = [len(x) for x in self.suits.values()]
        counts.sort()
        return len(self.suits) in [1, 2, 3] and counts[-1] >= 5

    def is_straight(self):
        ranks = self.ranks.keys()
        for i in range(len(ranks)):
           ranks[i] = self.as_int(ranks[i])

        ranks.sort()

        # Clear out and dupes we might have
        tmp_ranks = []
        for rank in ranks:
            if rank not in tmp_ranks:
                tmp_ranks.append(rank)
        ranks = tmp_ranks

        # Check for Ace being low case
        if ranks[0] == 2 and ranks[-1] == 14:
            log.debug("Found possible ace low straight")
            ranks = [1] + ranks[:-1]

        # The len math is here for dupes we removed and the low ace we
        # may have added
        for j in range(len(ranks) - 4):
            last = ranks[j]
            for i in range(j + 1, 5 + j):
                if last + 1 != ranks[i]:
                    break
                last += 1
            else:
                return True
        return False

    def is_trips(self):
        values = [len(x) for x in self.ranks.values()]
        values.sort()
        return values == [1, 1, 1, 1, 3]
   
    def is_two_pair(self):
        values = [len(x) for x in self.ranks.values()]
        values.sort()
        return values in [[1, 1, 1, 2, 2], [1, 2, 2, 2]]

    def is_one_pair(self):
        return len(self.ranks) == 6

    def as_int(self, rank):
        if rank == 'j':
            return 11
        elif rank == 'q':
            return 12
        elif rank == 'k':
            return 13
        elif rank == 'a':
            return 14
        else:
            return int(rank)

    def two_pair_value(self):
        hand_value = 0x200000
        doubles = []
        singles = []
        for key, value in self.ranks.iteritems():
            as_int = self.as_int(key)
            if len(value) == 2:
                doubles.append(as_int)
            else:
                singles.append(as_int)

        scale = 0x010000

        doubles.sort()
        doubles.reverse()
        for card in doubles:
            hand_value += scale * card
            scale /= 0x10

        # XXX this is just one card, but we should be able to make a method
        singles.sort()
        singles.reverse()
        for card in singles[:1]:
            hand_value += scale * card
            scale /= 0x10

        return hand_value

    def one_pair_value(self):
        hand_value = 0x100000
        singles = []
        for key, value in self.ranks.iteritems():
            as_int = self.as_int(key)
            if len(value) == 2:
                hand_value += 0x010000 * as_int
            else:
                singles.append(as_int)

        scale = 0x001000
        singles.sort()
        singles.reverse()
        for i in range(3):
            hand_value += scale * singles[i]
            scale /= 0x10

        return hand_value

    def single_value(self):
        hand_value = 0x000000
        singles = [self.as_int(x) for x in self.ranks.keys()]

        scale = 0x010000
        singles.sort()
        singles.reverse()
        for i in range(5):
            hand_value += scale * singles[i]
            scale /= 0x10

        return hand_value


    def _get_relative_value(self):
        """
        Arbitrary numeric weights assigned to hands for comparing
        """
        if self.is_royal():
            return 0x900000
        elif self.is_straight_flush():
            return 0x800000
        elif self.is_quads():
            return 0x700000
        elif self.is_full_house():
            return 0x600000
        elif self.is_flush():
            return 0x500000
        elif self.is_straight():
            return 0x400000
        elif self.is_trips():
            return 0x300000
        elif self.is_two_pair():
            return self.two_pair_value()
        elif self.is_one_pair():
            return self.one_pair_value()
        else:
            return self.single_value()

    def __gt__(self, other):
        return self._relative_value > other._relative_value


class PokerEval(object):

    def _is_royal(self, hand):
        royals = [[r + s for r in ranks[5:]] for s in suits]

        return hand in royals

    def winners(self, game=None, pockets=None, board=None):
        results = {}
        results['hi'] = []

        return results
