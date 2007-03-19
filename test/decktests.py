#!/usr/bin/env python

import unittest
import settestpath
from rounder.deck import OutOfCardsException
from rounder.deck import Deck

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
	    


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DeckTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
