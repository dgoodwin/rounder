#!/usr/bin/env python

import unittest
import rounder
import rounder.hand

from rounder.card import Card
from string import split

def getCards(handString):
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

def compareHands(expectedHandStr, resultHand):
    expectedHand = getCards(expectedHandStr)
    if (len(expectedHand) != 5 or len(resultHand) != 5):
        return False
    for i in range(len(expectedHand)):
        if expectedHand[i].rank != resultHand[i].rank:
            return False
        if expectedHand[i].suit != resultHand[i].suit:
            return False
    return True

def testHand(test, expected, initialCards, handRank=None):
    """
    Expected a reference to the calling test (so we can utilize the pyunit
    assertion methods), and two string representations of the hands in short
    notation. (ie. "Ac As Kd Ks 5h Td") The first represents the cards to
    populate the hand with, the second the expected outcome of the hand after
    processing.
    """
    resultsTuple = rounder.hand.finalEvaluate(getCards(initialCards))
    test.assert_(compareHands(expected, resultsTuple[1]))
    if handRank is not None:
        test.assertEqual(handRank, resultsTuple[0])

class HandTests(unittest.TestCase):

    def testCheckForStraight(self):
        """
        Check the hand processor's internal checkForStraight function, not
        actually testing the full hand ranking of straights just yet.
        """
        self.assert_(compareHands("Ac Kd Qh Js Tc",
            rounder.hand.checkForStraight(getCards("Ac Kd Qh Js Tc"))))
        self.assert_(compareHands("Ac Kd Qh Js Tc",
            rounder.hand.checkForStraight(getCards("Ac Kd Ks Qh Js Tc"))))
        self.assert_(compareHands("5s 4s 3s 2s As",
            rounder.hand.checkForStraight(getCards("As 8c 8s 7s 5s 4s 3s 2s"))))
        self.assert_(compareHands("9h 8h 7h 6h 5h",
            rounder.hand.checkForStraight(
                getCards("9h 9c 9s 8h 7h 6h 6c 5h 5c 5d"))))

    def testStraightFlushes(self):
        testHand(self, "Ts 9s 8s 7s 6s", "Ts 5c 6s 9h 6c 7s 8s 9s",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "As Ks Qs Js Ts", "8s 5c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "As Ks Qs Js Ts", "Ac Ad As Ks Qs Js 4c 9c 8s Td Ts",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "5c 4c 3c 2c Ac", "Ac 3c 2c 5c 4c",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "5c 4c 3c 2c Ac", "Ac 3c 2c 5c 3s 4c",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "As Ks Qs Js Ts", "Kc Qc Jc Tc 9c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        testHand(self, "As Ks Qs Js Ts", "Ac Kc Qc Jc Tc As Ks Js Qs Ts",
            rounder.hand.STRAIGHTFLUSH)

    def testQuads(self):
        testHand(self, "9c 9s 9h 9d As", "9c 9s 9h 9d Kd As",
            rounder.hand.FOUROFAKIND)
        testHand(self, "Ac As Ah Ad 5s", "Ac 2s As 2c Ah 5s Ad",
            rounder.hand.FOUROFAKIND)
        testHand(self, "Ac As Ah Ad Kc", "2d 2c 2h 2s Kc Ac As Ah Ad",
            rounder.hand.FOUROFAKIND)
        testHand(self, "2d 2s 2h 2c Ac", "Ac Ah As Kc 2d 2s 5h 2h 2c",
            rounder.hand.FOUROFAKIND)

    def testBoats(self):
        testHand(self, "Ac As Ad Kh Kc", "9d 8s 7h Ac Kh Kc As Ad",
            rounder.hand.FULLHOUSE)
        testHand(self, "2c 2d 2s 5h 5d", "2c 2d 2s 5h 5d",
            rounder.hand.FULLHOUSE)
        testHand(self, "8c 8s 8d Ah Ac", "Ah Ac 8c 8s 8d",
            rounder.hand.FULLHOUSE)
        testHand(self, "Ks Kc Kd 2c 2d", "5h 6h Ac 2c 9h 2d Ks Th Kc 7s Kd",
            rounder.hand.FULLHOUSE)
        testHand(self, "Ac As Ah Kh Kd", "Ac As Ah Kh Kd Kc Qh Qd",
            rounder.hand.FULLHOUSE)

    def testFlushes(self):
        testHand(self, "Ah Kh 4h 3h 2h", "Kh 3h 4h 2h Ah",
            rounder.hand.FLUSH)
        testHand(self, "8h 7h 5h 3h 2h", "Ac Kc As 8h 2h 9d 5h 7h 7d 3h",
            rounder.hand.FLUSH)
        testHand(self, "As Ks 9s 8s 2s", "Kh Qh Th 3h 2h As 8s 9s 2s Ks",
            rounder.hand.FLUSH)

    def testStraights(self):
        testHand(self, "Ac Ks Qh Jd Ts", "Ts Jd Qh Ks Ac",
            rounder.hand.STRAIGHT)
        testHand(self, "Ac Ks Qh Jd Tc", "2c 2s 3h Ac Tc Ts Qh Jd Ks",
            rounder.hand.STRAIGHT)
        testHand(self, "5h 4c 3h 2h Ah", "Ah Kc Qd Jd 4c 3h 2h 5h",
            rounder.hand.STRAIGHT)
        testHand(self, "8c 7h 6d 5s 4c", "Tc Js 8c 4c 5s 5h 6d 7h",
            rounder.hand.STRAIGHT)

    def testTrips(self):
        testHand(self, "Ac As Ad Ks Qh", "Ac 2h Qh Ks As 3h Ad",
            rounder.hand.THREEOFAKIND)
        testHand(self, "2c 2s 2d 8h 7d", "2c 2s 5h 7d 8h 2d",
            rounder.hand.THREEOFAKIND)

    def testTwoPairs(self):
        testHand(self, "Ac As Kh Kd Qs", "4d Kh Qs 8h 8s Ac Kd As 2h 3h",
            rounder.hand.TWOPAIR)
        testHand(self, "8s 8c 7s 7c Ad", "Ad 7s 6c 6s 7c 8s 8c Kd",
            rounder.hand.TWOPAIR)

    def testOnePairs(self):
        testHand(self, "Ac As Kd Qh 8s", "Kd Qh 7s 4d Ac As 8s 3h",
            rounder.hand.ONEPAIR)

    def testNoPairs(self):
        testHand(self, "Ac Kh Jd Ts 5h", "5h 3c 2s Kh Jd Ts Ac",
            rounder.hand.HIGHCARD)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HandTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
