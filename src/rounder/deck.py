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

""" Rounder module representing a deck of cards. """

import rounder.card

from logging import getLogger
logger = getLogger("rounder.deck")

from random import shuffle
from rounder.card import Card
from rounder.core import RounderException

class OutOfCardsException(RounderException):

    """
    Thrown when someone tries to draw a card from the deck, but there aren't
    any left.
    """
    
    def __init__(self):
        self.value = "Ran out of cards."

    def __str__(self):
        return repr(self.value)



class Deck:

    """ Standard 52 card deck. """

    def __init__(self):
        self.cards = []
        for i in rounder.card.ALL_SUITS:
            for j in range(2, 15):
                self.cards.append(Card(j, i))
        self.__topCard = 0

    def __str__(self):
        output = "\n"
        i = 0
        for card in self.cards:
            output = output + str(card) + " "
            if ((i+1) % 13 == 0 and i != 0):
                output += "\n"
            i += 1
        output += "\n"
        return output
    
    def shuffle(self):
        """ Shuffle the deck. """
        # TODO: Currently this uses the list shuffle method. Alot of room for
        # improvement here to simulate more realistic shuffling events.
        shuffle(self.cards)
        self.__topCard = 0

    def draw_card(self):
        """ Returns a reference to the top card on the deck. """
        if (self.__topCard >= 52):
            raise OutOfCardsException()
        c = self.cards[self.__topCard]
        self.__topCard += 1
        return c
    
    def has_more_cards(self):
        if self.__topCard < 52:
            return True
        return False
