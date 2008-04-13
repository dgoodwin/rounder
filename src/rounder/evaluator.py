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
       return self.is_straight(suit_matters=True, ace_high_matters=True)

    def is_straight_flush(self):
        return self.is_straight(suit_matters=True)

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

    def is_straight(self, suit_matters=False, ace_high_matters=False):
        # XXX This needs cleanup, esp for these extra arguments
        ranks = []
        for key, value in self.ranks.iteritems():
           ranks.append((self.as_int(key), value))

        ranks.sort(cmp=lambda x, y: cmp(x[0], y[0]))

        # Check for Ace being low case
        if ranks[0][0] == 2 and ranks[-1][0] == 14:
            log.debug("Found possible ace low straight")
            ranks = [(1, ranks[-1][1])] + ranks[:-1]

        # The len math is here for dupes we removed and the low ace we
        # may have added
        for j in range(len(ranks) - 4):
            last = ranks[j]
            suit_hash = {'s' : 0, 'c' : 0, 'd' : 0, 'h' : 0}
            for suit in last[1]:
                suit_hash[suit] += 1

            for i in range(j + 1, 5 + j):
                if last[0] + 1 != ranks[i][0]:
                    break
                for suit in ranks[i][1]:
                    suit_hash[suit] += 1
                last = ranks[i]
            else:
                if ace_high_matters and last[0] != 14:
                    continue
                if suit_matters:
                    for value in suit_hash.itervalues():
                        if value == 5:
                            return True
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

    @staticmethod
    def _compute_card_values(cards, count, scale):
        hand_value = 0x0

        cards.sort(reverse=True)
        for card in cards[:count]:
            hand_value += scale * card
            scale /= 0x10

        return hand_value

    def royal_value(self):
        # Only one royal flush, so only one value
        hand_value = 0x900000
        return hand_value

    def straight_flush_value(self):
        # XXX Implement me
        hand_value = 0x800000
        return hand_value

    def quads_value(self):
        hand_value = 0x700000

        quads = []
        singles = []
        for key, value in self.ranks.iteritems():
            as_int = self.as_int(key)
            if len(value) == 4:
                quads.append(as_int)
            else:
                singles.append(as_int)

        hand_value += self._compute_card_values(quads, 1, 0x010000)
        hand_value += self._compute_card_values(singles, 1, 0x001000)

        return hand_value

    def full_house_value(self):
        # XXX Implement me
        hand_value = 0x600000
        return hand_value

    def flush_value(self):
        hand_value = 0x500000
        for suit, ranks in self.suits.iteritems():
            if len(ranks) >= 5:
                new_ranks = [self.as_int(rank) for rank in ranks]
                hand_value += self._compute_card_values(new_ranks, 5, 0x010000)
                break
        return hand_value

    def straight_value(self):
        hand_value = 0x400000

        singles = []
        for key, value in self.ranks.iteritems():
            as_int = self.as_int(key)
            if len(value) == 1:
                singles.append(as_int)

        singles.sort()

        if singles[-1] == self.as_int('a') and singles[-2] != self.as_int('k'):
            highest = singles[-2]
        else:
            highest = singles[-1]

        hand_value += highest * 0x010000

        return hand_value

    def trips_value(self):
        hand_value = 0x300000
        triples = []
        singles = []
        for key, value in self.ranks.iteritems():
            as_int = self.as_int(key)
            if len(value) == 3:
                triples.append(as_int)
            else:
                singles.append(as_int)

        hand_value += self._compute_card_values(triples, 1, 0x010000)
        hand_value += self._compute_card_values(singles, 2, 0x001000)

        return hand_value

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

        hand_value += self._compute_card_values(doubles, 2, 0x010000)
        hand_value += self._compute_card_values(singles, 1, 0x000100)

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

        hand_value += self._compute_card_values(singles, 3, 0x001000)

        return hand_value

    def single_value(self):
        hand_value = 0x000000
        singles = [self.as_int(x) for x in self.ranks.keys()]

        hand_value += self._compute_card_values(singles, 5, 0x010000)

        return hand_value


    def _get_relative_value(self):
        """
        Arbitrary numeric weights assigned to hands for comparing
        """
        if self.is_royal():
            return self.royal_value()
        elif self.is_straight_flush():
            return self.straight_flush_value()
        elif self.is_quads():
            return self.quads_value()
        elif self.is_full_house():
            return self.full_house_value()
        elif self.is_flush():
            return self.flush_value()
        elif self.is_straight():
            return self.straight_value()
        elif self.is_trips():
            return self.trips_value()
        elif self.is_two_pair():
            return self.two_pair_value()
        elif self.is_one_pair():
            return self.one_pair_value()
        else:
            return self.single_value()

    def __cmp__(self, other):
        return cmp(self._relative_value, other._relative_value)


class PokerEval(object):

    def _is_royal(self, hand):
        royals = [[r + s for r in ranks[5:]] for s in suits]

        return hand in royals

    def winners(self, game=None, pockets=None, board=None):
        results = {}
        results['hi'] = []

        return results
