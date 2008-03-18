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


class FullHand(object):

    def __init__(self, hand, table):
        fullhand = hand + table
        fullhand = list(fullhand)
        fullhand.sort()
        self.cards = fullhand

        self._relative_value = self._get_relative_value()

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
        ranks = {}
        for card in self.cards:
            rank = card[:-1]
            if not ranks.has_key(rank):
                ranks[rank] = []
            ranks[rank].append(card[-1])
        return len(ranks) == 2 and len(ranks.values()[0]) in [1, 4]

    def is_full_house(self):
        ranks = set()
        for card in self.cards:
            ranks.add(card[:-1])
        return len(ranks) == 2

    def is_flush(self):
        suits = set()
        for card in self.cards:
            suits.add(card[-1])
        return len(suits) == 1

    def is_straight(self):
        ranks = [card[:-1] for card in self.cards]
        for i in range(len(ranks)):
            if ranks[i] == 'j':
                ranks[i] = 11
            elif ranks[i] == 'q':
                ranks[i] = 12
            elif ranks[i] == 'k':
                ranks[i] = 13
            elif ranks[i] == 'a':
                ranks[i] = 14

            ranks[i] = int(ranks[i])

        ranks.sort()

        last = ranks[0]

        # Check for Ace being low case
        if last == 2:
            if ranks[-1] == 14:
                last = 1
                ranks = [1] + ranks[:-1]

        for i in range(1, len(ranks)):
            if last + 1 != ranks[i]:
                return False
            last += 1
        return True

    def is_trips(self):
        ranks = {}
        for card in self.cards:
            rank = card[:-1]
            if not ranks.has_key(rank):
                ranks[rank] = []
            ranks[rank].append(card[-1])
        values = [len(x) for x in ranks.values()]
        values.sort()
        return len(ranks) == 3 and values == [1, 1, 3]
   
    def is_two_pair(self):
        ranks = {}
        for card in self.cards:
            rank = card[:-1]
            if not ranks.has_key(rank):
                ranks[rank] = []
            ranks[rank].append(card[-1])
        values = [len(x) for x in ranks.values()]
        values.sort()
        return len(ranks) == 3 and values == [1, 2, 2]

    def is_one_pair(self):
        ranks = set()
        for card in self.cards:
            ranks.add(card[:-1])
        return len(ranks) == 4

    def _get_relative_value(self):
        """
        Arbitrary numeric weights assigned to hands for comparing
        """
        if self.is_royal():
            return 1000
        elif self.is_straight_flush():
            return 900
        elif self.is_quads():
            return 800
        elif self.is_full_house():
            return 700
        elif self.is_flush():
            return 600
        elif self.is_straight():
            return 500
        elif self.is_trips():
            return 400
        elif self.is_two_pair():
            return 300
        elif self.is_one_pair():
            return 200
        else:
            return 0

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
