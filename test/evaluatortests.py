
import unittest

import settestpath

from rounder.evaluator import FullHand


class FullHandTests(unittest.TestCase):

    def testIsRoyal(self):
        hand = FullHand(('ad', 'kd'), ('qd', 'jd', '10d'))
        self.assertTrue(hand.is_royal())

    def testIsRoyalNotRoyal(self):
        hand = FullHand(('as', 'kd'), ('qd', 'jd', '10d'))
        self.assertFalse(hand.is_royal())

    def testIsFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'js', '4s'))
        self.assertTrue(hand.is_flush())

    def testIsNotFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_flush())

    def testIsOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'ad', '4s'))
        self.assertTrue(hand.is_one_pair())

    def testIsNotOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_one_pair())

    def testIsFullHouse(self):
        hand = FullHand(('as', 'ks'), ('kd', 'ad', 'ac'))
        self.assertTrue(hand.is_full_house())

    def testIsNotFullHouse(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_full_house())

    def testIsQuads(self):
        hand = FullHand(('as', 'ks'), ('ad', 'ac', 'ah'))
        self.assertTrue(hand.is_quads())

    def testIsNotQuads(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_quads())

        hand = FullHand(('9c', '9s'), ('qs', 'qd', 'qh'))
        self.assertFalse(hand.is_quads())

    def testIsTwoPair(self):
        hand = FullHand(('as', 'ks'), ('ad', 'kc', '9h'))
        self.assertTrue(hand.is_two_pair())

    def testIsNotTwoPair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_two_pair())

    def testIsTrips(self):
        hand = FullHand(('as', 'js'), ('ad', 'kc', 'ac'))
        self.assertTrue(hand.is_trips())

    def testIsNotTrips(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_trips())

    def testIsStraight(self):
        hand = FullHand(('as', 'js'), ('qd', 'kc', '10c'))
        self.assertTrue(hand.is_straight())

    def testIsNotStraight(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_straight())

    def testIsStraightAceLow(self):
        hand = FullHand(('as', '3s'), ('2d', '4c', '5c'))
        self.assertTrue(hand.is_straight())

    def testIsStraightFlush(self):
        hand = FullHand(('9s', 'js'), ('10s', 'ks', 'qs'))
        self.assertTrue(hand.is_straight())

    def testIsNotStraightFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s'))
        self.assertFalse(hand.is_straight())

    def testRoyalGreaterThanStraightFlush(self):
        board = ('qs', 'js', '10s')
        hand1 = FullHand(('as', 'ks'), board)
        hand2 = FullHand(('9s', '8s'), board)

        self.assertTrue(hand1 > hand2)

    def testStraightFlushGreaterThanQuads(self):
        hand1 = FullHand(('as', 'ks'), ('qs', 'js', '10s'))
        hand2 = FullHand(('9s', '8s'), ('9d', '9h', '9c'))

        self.assertTrue(hand1 > hand2)

    def testQuadsGreaterThanFullHouse(self):
        board = ('ks', 'kd', 'kh')
        hand1 = FullHand(('as', 'kc'), board)
        hand2 = FullHand(('9s', '9d'), board)

        self.assertTrue(hand1.is_quads())
        self.assertTrue(hand2.is_full_house())
        self.assertFalse(hand2.is_quads())
        self.assertTrue(hand1 > hand2)

    def testFullHouseGreaterThanFlush(self):
        board = ('ks', 'kd', 'kh')
        hand1 = FullHand(('9s', '9d'), board)
        hand2 = FullHand(('as', '9s'), ('7s', '4s', '2s'))
        
        self.assertTrue(hand1 > hand2)

    def testFlushGreaterThanStraight(self):
        board = ('6s', '4s', '2s')
        hand1 = FullHand(('as', '9s'), board) 
        hand2 = FullHand(('3s', '5d'), board)
        
        self.assertTrue(hand1 > hand2)

    def testStraightGreaterThanTrips(self):
        board = ('6s', '4s', '2s')
        hand1 = FullHand(('3s', '5d'), board)
        hand2 = FullHand(('4h', '4d'), board) 
        
        self.assertTrue(hand1 > hand2)

    def testTripsGreaterThanTwoPair(self):
        board = ('6s', '4s', '2s')
        hand1 = FullHand(('4h', '4d'), board) 
        hand2 = FullHand(('6d', '4h'), board)
        
        self.assertTrue(hand1 > hand2)

    def testTwoPairGreaterThanOnePair(self):
        board = ('6s', '4s', '2s')
        hand1 = FullHand(('6d', '4h'), board)
        hand2 = FullHand(('4h', '7d'), board) 
        
        self.assertTrue(hand1 > hand2)

    def testOnePairGreaterThanHighCard(self):
        board = ('6s', '4s', '2s')
        hand1 = FullHand(('4h', '7d'), board) 
        hand2 = FullHand(('7d', 'kh'), board)
        
        self.assertTrue(hand1 > hand2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FullHandTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
