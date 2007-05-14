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

import rounder
import rounder.hand

from string import split

from rounder.card import Card
from rounder.player import Player
from rounder.hand import DefaultHandProcessor
from rounder.hand import check_for_straight

from utils import create_players_list

CHIPS = 1000

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

class DetermineWinnerTests(unittest.TestCase):

    def setUp(self):
        self.players = create_players_list(2, CHIPS)
        self.processor = DefaultHandProcessor()

    def test_easy_case(self):
        community_cards = " 5c 3c"
        eval_results = self.processor.evaluate(
            get_cards("3s 3d 7s 9s Jd" + community_cards))
        self.players[0].final_hand_rank = eval_results[0]
        self.players[0].final_hand = eval_results[1]

        eval_results = self.processor.evaluate(
            get_cards("2s 2d 8s Tc Ad" + community_cards))
        self.players[1].final_hand_rank = eval_results[0]
        self.players[1].final_hand = eval_results[1]

        winners = self.processor.determine_winners(self.players)
        self.assertEquals(1, len(winners))
        self.assertEqual(self.players[0], winners[0])
        self.assertEqual(rounder.hand.THREEOFAKIND, winners[0].final_hand_rank)



class HandTests(unittest.TestCase):

    def setUp(self):
        self.processor = DefaultHandProcessor()

    def verify_hand(self, expected, initialCards, handRank=None):
        """
        Verify that the expected hand is produced from the given cards, and
        evaluates to the expected hand rank. Hands are provided in the
        shorthand string notation. (ie. "Ac As Kd Ks 5h Td") 
        """
        resultsTuple = self.processor.evaluate(get_cards(initialCards))
        self.assert_(compare_hands(expected, resultsTuple[1]))
        if handRank is not None:
            self.assertEqual(handRank, resultsTuple[0])

    def test_check_for_straight(self):
        """
        Check the hand processor's internal check_for_straight function, not
        actually testing the full hand ranking of straights just yet.
        """
        self.assert_(compare_hands("Ac Kd Qh Js Tc",
            check_for_straight(get_cards("Ac Kd Qh Js Tc"))))
        self.assert_(compare_hands("Ac Kd Qh Js Tc",
            check_for_straight(get_cards("Ac Kd Ks Qh Js Tc"))))
        self.assert_(compare_hands("5s 4s 3s 2s As",
            check_for_straight(get_cards(
                "As 8c 8s 7s 5s 4s 3s 2s"))))
        self.assert_(compare_hands("9h 8h 7h 6h 5h",
            check_for_straight(
                get_cards("9h 9c 9s 8h 7h 6h 6c 5h 5c 5d"))))

    def testStraightFlushes(self):
        self.verify_hand("Ts 9s 8s 7s 6s", "Ts 5c 6s 9h 6c 7s 8s 9s",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("As Ks Qs Js Ts", "8s 5c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("As Ks Qs Js Ts", "Ac Ad As Ks Qs Js 4c 9c 8s Td Ts",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("5c 4c 3c 2c Ac", "Ac 3c 2c 5c 4c",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("5c 4c 3c 2c Ac", "Ac 3c 2c 5c 3s 4c",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("As Ks Qs Js Ts", "Kc Qc Jc Tc 9c As Ks Qs Js Ts",
            rounder.hand.STRAIGHTFLUSH)
        self.verify_hand("As Ks Qs Js Ts", "Ac Kc Qc Jc Tc As Ks Js Qs Ts",
            rounder.hand.STRAIGHTFLUSH)

    def testQuads(self):
        self.verify_hand("9c 9s 9h 9d As", "9c 9s 9h 9d Kd As",
            rounder.hand.FOUROFAKIND)
        self.verify_hand("Ac As Ah Ad 5s", "Ac 2s As 2c Ah 5s Ad",
            rounder.hand.FOUROFAKIND)
        self.verify_hand("Ac As Ah Ad Kc", "2d 2c 2h 2s Kc Ac As Ah Ad",
            rounder.hand.FOUROFAKIND)
        self.verify_hand("2d 2s 2h 2c Ac", "Ac Ah As Kc 2d 2s 5h 2h 2c",
            rounder.hand.FOUROFAKIND)

    def testBoats(self):
        self.verify_hand("Ac As Ad Kh Kc", "9d 8s 7h Ac Kh Kc As Ad",
            rounder.hand.FULLHOUSE)
        self.verify_hand("2c 2d 2s 5h 5d", "2c 2d 2s 5h 5d",
            rounder.hand.FULLHOUSE)
        self.verify_hand("8c 8s 8d Ah Ac", "Ah Ac 8c 8s 8d",
            rounder.hand.FULLHOUSE)
        self.verify_hand("Ks Kc Kd 2c 2d", "5h 6h Ac 2c 9h 2d Ks Th Kc 7s Kd",
            rounder.hand.FULLHOUSE)
        self.verify_hand("Ac As Ah Kh Kd", "Ac As Ah Kh Kd Kc Qh Qd",
            rounder.hand.FULLHOUSE)

    def testFlushes(self):
        self.verify_hand("Ah Kh 4h 3h 2h", "Kh 3h 4h 2h Ah",
            rounder.hand.FLUSH)
        self.verify_hand("8h 7h 5h 3h 2h", "Ac Kc As 8h 2h 9d 5h 7h 7d 3h",
            rounder.hand.FLUSH)
        self.verify_hand("As Ks 9s 8s 2s", "Kh Qh Th 3h 2h As 8s 9s 2s Ks",
            rounder.hand.FLUSH)

    def testStraights(self):
        self.verify_hand("Ac Ks Qh Jd Ts", "Ts Jd Qh Ks Ac",
            rounder.hand.STRAIGHT)
        self.verify_hand("Ac Ks Qh Jd Tc", "2c 2s 3h Ac Tc Ts Qh Jd Ks",
            rounder.hand.STRAIGHT)
        self.verify_hand("5h 4c 3h 2h Ah", "Ah Kc Qd Jd 4c 3h 2h 5h",
            rounder.hand.STRAIGHT)
        self.verify_hand("8c 7h 6d 5s 4c", "Tc Js 8c 4c 5s 5h 6d 7h",
            rounder.hand.STRAIGHT)

    def testTrips(self):
        self.verify_hand("Ac As Ad Ks Qh", "Ac 2h Qh Ks As 3h Ad",
            rounder.hand.THREEOFAKIND)
        self.verify_hand("2c 2s 2d 8h 7d", "2c 2s 5h 7d 8h 2d",
            rounder.hand.THREEOFAKIND)

    def testTwoPairs(self):
        self.verify_hand("Ac As Kh Kd Qs", "4d Kh Qs 8h 8s Ac Kd As 2h 3h",
            rounder.hand.TWOPAIR)
        self.verify_hand("8s 8c 7s 7c Ad", "Ad 7s 6c 6s 7c 8s 8c Kd",
            rounder.hand.TWOPAIR)

    def testOnePairs(self):
        self.verify_hand("Ac As Kd Qh 8s", "Kd Qh 7s 4d Ac As 8s 3h",
            rounder.hand.ONEPAIR)

    def testNoPairs(self):
        self.verify_hand("Ac Kh Jd Ts 5h", "5h 3c 2s Kh Jd Ts Ac",
            rounder.hand.HIGHCARD)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HandTests))
    suite.addTest(unittest.makeSuite(DetermineWinnerTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
