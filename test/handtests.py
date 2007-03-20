#!/usr/bin/env python

import unittest
import rounder
import rounder.hand

from rounder.card import Card
from string import split

def get_cards(handString):
    """
    Create a list of card objects corresponding to the shorthand strings
    provided. (i.e. Ac, Kd, 2s, etc.)
    """
    cardStrings = split(handString, " ")
    cardList = []
    for c in cardStrings:
        cardList.append(Card(c))
    return cardList

#def getHand(handString):
#    hand = rounder.ai.base.Hand()
#    cardStrings = split(handString, " ")
#    for c in cardStrings:
#        hand.addCard(Card(c))
#    return hand

def compare_hands(expectedHandStr, resultHand):
    expectedHand = get_cards(expectedHandStr)
    if (len(expectedHand) != 5 or len(resultHand) != 5):
        return False
    for i in range(len(expectedHand)):
        if expectedHand[i].rank != resultHand[i].rank:
            return False
        if expectedHand[i].suit != resultHand[i].suit:
            return False
    return True

def test_hand(test, expected, initialCards, handRank=None):
    """
    Expected a reference to the calling test (so we can utilize the pyunit
    assertion methods), and two string representations of the hands in short
    notation. (ie. "Ac As Kd Ks 5h Td") The first represents the cards to
    populate the hand with, the second the expected outcome of the hand after
    processing.
    """
    resultsTuple = rounder.hand.final_evaluate(get_cards(initialCards))
    test.assert_(compare_hands(expected, resultsTuple[1]))
    if handRank is not None:
        test.assertEqual(handRank, resultsTuple[0])

class HandTests(unittest.TestCase):

    def testcheck_for_straight(self):
        """
        Check the hand processor's internal check_for_straight function, not
        actually testing the full hand ranking of straights just yet.
        """
        self.assert_(compare_hands("Ac Kd Qh Js Tc",
            rounder.hand.check_for_straight(get_cards("Ac Kd Qh Js Tc"))))
        self.assert_(compare_hands("Ac Kd Qh Js Tc",
            rounder.hand.check_for_straight(get_cards("Ac Kd Ks Qh Js Tc"))))
        self.assert_(compare_hands("5s 4s 3s 2s As",
            rounder.hand.check_for_straight(get_cards("As 8c 8s 7s 5s 4s 3s 2s"))))
        self.assert_(compare_hands("9h 8h 7h 6h 5h",
            rounder.hand.check_for_straight(
                get_cards("9h 9c 9s 8h 7h 6h 6c 5h 5c 5d"))))

    def testStraightFlushes(self):
        test_hand(self, "Ts 9s 8s 7s 6s", "Ts 5c 6s 9h 6c 7s 8s 9s",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "As Ks Qs Js Ts", "8s 5c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "As Ks Qs Js Ts", "Ac Ad As Ks Qs Js 4c 9c 8s Td Ts",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "5c 4c 3c 2c Ac", "Ac 3c 2c 5c 4c",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "5c 4c 3c 2c Ac", "Ac 3c 2c 5c 3s 4c",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "As Ks Qs Js Ts", "Kc Qc Jc Tc 9c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        test_hand(self, "As Ks Qs Js Ts", "Ac Kc Qc Jc Tc As Ks Js Qs Ts",
            rounder.hand.STRAIGHTFLUSH)

    def testQuads(self):
        test_hand(self, "9c 9s 9h 9d As", "9c 9s 9h 9d Kd As",
            rounder.hand.FOUROFAKIND)
        test_hand(self, "Ac As Ah Ad 5s", "Ac 2s As 2c Ah 5s Ad",
            rounder.hand.FOUROFAKIND)
        test_hand(self, "Ac As Ah Ad Kc", "2d 2c 2h 2s Kc Ac As Ah Ad",
            rounder.hand.FOUROFAKIND)
        test_hand(self, "2d 2s 2h 2c Ac", "Ac Ah As Kc 2d 2s 5h 2h 2c",
            rounder.hand.FOUROFAKIND)

    def testBoats(self):
        test_hand(self, "Ac As Ad Kh Kc", "9d 8s 7h Ac Kh Kc As Ad",
            rounder.hand.FULLHOUSE)
        test_hand(self, "2c 2d 2s 5h 5d", "2c 2d 2s 5h 5d",
            rounder.hand.FULLHOUSE)
        test_hand(self, "8c 8s 8d Ah Ac", "Ah Ac 8c 8s 8d",
            rounder.hand.FULLHOUSE)
        test_hand(self, "Ks Kc Kd 2c 2d", "5h 6h Ac 2c 9h 2d Ks Th Kc 7s Kd",
            rounder.hand.FULLHOUSE)
        test_hand(self, "Ac As Ah Kh Kd", "Ac As Ah Kh Kd Kc Qh Qd",
            rounder.hand.FULLHOUSE)

    def testFlushes(self):
        test_hand(self, "Ah Kh 4h 3h 2h", "Kh 3h 4h 2h Ah",
            rounder.hand.FLUSH)
        test_hand(self, "8h 7h 5h 3h 2h", "Ac Kc As 8h 2h 9d 5h 7h 7d 3h",
            rounder.hand.FLUSH)
        test_hand(self, "As Ks 9s 8s 2s", "Kh Qh Th 3h 2h As 8s 9s 2s Ks",
            rounder.hand.FLUSH)

    def testStraights(self):
        test_hand(self, "Ac Ks Qh Jd Ts", "Ts Jd Qh Ks Ac",
            rounder.hand.STRAIGHT)
        test_hand(self, "Ac Ks Qh Jd Tc", "2c 2s 3h Ac Tc Ts Qh Jd Ks",
            rounder.hand.STRAIGHT)
        test_hand(self, "5h 4c 3h 2h Ah", "Ah Kc Qd Jd 4c 3h 2h 5h",
            rounder.hand.STRAIGHT)
        test_hand(self, "8c 7h 6d 5s 4c", "Tc Js 8c 4c 5s 5h 6d 7h",
            rounder.hand.STRAIGHT)

    def testTrips(self):
        test_hand(self, "Ac As Ad Ks Qh", "Ac 2h Qh Ks As 3h Ad",
            rounder.hand.THREEOFAKIND)
        test_hand(self, "2c 2s 2d 8h 7d", "2c 2s 5h 7d 8h 2d",
            rounder.hand.THREEOFAKIND)

    def testTwoPairs(self):
        test_hand(self, "Ac As Kh Kd Qs", "4d Kh Qs 8h 8s Ac Kd As 2h 3h",
            rounder.hand.TWOPAIR)
        test_hand(self, "8s 8c 7s 7c Ad", "Ad 7s 6c 6s 7c 8s 8c Kd",
            rounder.hand.TWOPAIR)

    def testOnePairs(self):
        test_hand(self, "Ac As Kd Qh 8s", "Kd Qh 7s 4d Ac As 8s 3h",
            rounder.hand.ONEPAIR)

    def testNoPairs(self):
        test_hand(self, "Ac Kh Jd Ts 5h", "5h 3c 2s Kh Jd Ts Ac",
            rounder.hand.HIGHCARD)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HandTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
