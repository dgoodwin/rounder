#!/usr/bin/env python

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

import unittest
from rounder.deck import OutOfCardsException
from rounder.deck import Deck
from utils import *


#Deck Utiltiy methods useful for testing


class DeckTests(unittest.TestCase):

    def test_out_of_cards(self):
        """ Ensure the deck won't let us draw too many cards """
        self.assertRaises(OutOfCardsException, self.draw_too_many_cards)

    def test_has_more_cards(self):
        d = Deck()
        c = []
        while d.has_more_cards():
            c.append(d.draw_card())
        self.assertEquals(52, len(c))

    def draw_too_many_cards(self):
        d = Deck()
        for i in range(0, 53):
            d.draw_card()


class DeckTestUtilsTests(unittest.TestCase):

    def test_reorder_deck_one(self):
        deck = Deck()
        cards = create_cards_from_list(['Ad', 'As', 'Ah'])
        reorder_deck(deck, cards)

        for i in range(3):
            self.assertEquals(deck.cards[i], cards[i], "Card %d incorrect" % i)

        for i in range(3, 52):
            for j in range(3):
                self.assertNotEquals(deck.cards[i], cards[j],
                    "Card %d in deck twice" % j)


