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

""" Tests for the rounder.card module. """

import unittest

import settestpath

from rounder.card import SPADE
from rounder.card import DIAMOND
from rounder.card import HEART
from rounder.card import CLUB

from rounder.card import Card
from rounder.core import RounderException

from utils import *

class CardTests(unittest.TestCase):

    def testCreateCardByString(self):
        self.__testCard(Card('2s'), 2, SPADE)
        self.__testCard(Card('Ad'), 14, DIAMOND)
        self.__testCard(Card('4', 'c'), 4, CLUB)
        self.__testCard(Card(14, 'h'), 14, HEART)
        self.__testCard(Card(13, SPADE), 13, SPADE)

    def __testCard(self, card, rank, suit):
        self.assertEquals(card.rank, rank)
        self.assertEquals(card.suit, suit)

    def testToString(self):
        c = Card(2, CLUB)
        self.assertEqual("2c", str(c))
        c = Card(14, SPADE)
        self.assertEqual("As", str(c))

    def testInvalidCards(self):
        self.assertRaises(RounderException, Card, 1, CLUB)
        self.assertRaises(RounderException, Card, 15, CLUB)

    def testGetCard(self):
        # TODO: move these to a base class
        aceOfSpades = Card("As")
        self.assertEquals("As", str(aceOfSpades))

        tenOfClubs = Card("Tc")
        self.assertEquals("Tc", str(tenOfClubs))

        twoOfHearts = Card("2h")
        self.assertEquals("2h", str(twoOfHearts))

        sixOfDiamonds = Card("6d")
        self.assertEquals("6d", str(sixOfDiamonds))

        kingOfHearts = Card("Kh")
        self.assertEquals("Kh", str(kingOfHearts))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CardTests))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
