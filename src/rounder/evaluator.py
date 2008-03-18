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

suits = ('s', 'c', 'h', 'd')
ranks = [str(x) for x in range(2, 11)] + ['j', 'q', 'k', 'a']

royals = [[r + s for r in ranks[-5:]] for s in suits]
for hand in royals:
    hand.sort()

class FullHand(object):

    def __init__(self, hand, table):
        fullhand = hand + table
        fullhand = list(fullhand)
        fullhand.sort()
        self.cards = fullhand

    def is_royal(self):
        for hand in royals:
            if hand == self.cards:
                return True
        return False

    def is_flush(self):
        suits = set()
        for card in self.cards:
            suits.add(card[-1])
        return len(suits) == 1

    def is_one_pair(self):
        ranks = set()
        for card in self.cards:
            ranks.add(card[:-1])
        return len(ranks) == 4

    def is_full_house(self):
        ranks = set()
        for card in self.cards:
            ranks.add(card[:-1])
        return len(ranks) == 2



class PokerEval(object):

    def _is_royal(self, hand):
        royals = [[r + s for r in ranks[5:]] for s in suits]

        return hand in royals

    def winners(self, game=None, pockets=None, board=None):
        results = {}
        results['hi'] = []

        return results