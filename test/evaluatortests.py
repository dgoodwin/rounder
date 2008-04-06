
import unittest

import settestpath

from rounder.evaluator import FullHand


class FullHandTests(unittest.TestCase):

    def assertHandGreaterThan(self, hand1, hand2):
        if not hand1 > hand2:
            self.fail("0x%.6X not greater than 0x%.6X" %
                    (hand1._relative_value, hand2._relative_value))

    def testIsRoyal(self):
        hand = FullHand(('ad', 'kd'), ('qd', 'jd', '10d', '10s', '7h'))
        self.assertTrue(hand.is_royal())

    def testIsRoyalNotRoyal(self):
        hand = FullHand(('as', 'kd'), ('qd', 'jd', '10d', '10s', '7h'))
        self.assertFalse(hand.is_royal())

    def testIsFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'js', '4s', '6c', 'jd'))
        self.assertTrue(hand.is_flush())

    def testIsNotFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6c', '8h'))
        self.assertFalse(hand.is_flush())

    def testIsOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'ad', '4s', '6h', '8c'))
        self.assertTrue(hand.is_one_pair())

    def testIsNotOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6h', '8c'))
        self.assertFalse(hand.is_one_pair())

    def testIsFullHouse(self):
        hand = FullHand(('as', 'ks'), ('kd', 'ad', 'ac', '10d', '9s'))
        self.assertTrue(hand.is_full_house())

    def testIsNotFullHouse(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '9s'))
        self.assertFalse(hand.is_full_house())

    def testIsQuads(self):
        hand = FullHand(('as', 'ks'), ('ad', 'ac', 'ah', '10d', '9s'))
        self.assertTrue(hand.is_quads())

    def testIsNotQuads(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '8c'))
        self.assertFalse(hand.is_quads())

        hand = FullHand(('9c', '9s'), ('qs', 'qd', 'qh', '10d', '8c'))
        self.assertFalse(hand.is_quads())

    def testIsTwoPair(self):
        hand = FullHand(('as', 'ks'), ('ad', 'kc', '9h', 'jd', '5c'))
        self.assertTrue(hand.is_two_pair())

    def testIsNotTwoPair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6s', '7h'))
        self.assertFalse(hand.is_two_pair())

    def testIsTrips(self):
        hand = FullHand(('as', 'js'), ('ad', 'kc', 'ac', '10d', '9s'))
        self.assertTrue(hand.is_trips())

    def testIsNotTrips(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '8s'))
        self.assertFalse(hand.is_trips())

    def testIsStraight(self):
        hand = FullHand(('as', 'js'), ('qd', 'kc', '10c', '4h', '4h'))
        self.assertTrue(hand.is_straight())

    def testIsNotStraight(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '4h', '6c'))
        self.assertFalse(hand.is_straight())

        hand = FullHand(('qh', '4d'), ('as', '5s', 'js', '10c', '9d'))
        self.assertFalse(hand.is_straight())

    def testIsStraightAceLow(self):
        hand = FullHand(('as', '3s'), ('2d', '4c', '5c', 'kd', '6c'))
        self.assertTrue(hand.is_straight())

    def testIsStraightFlush(self):
        hand = FullHand(('9s', 'js'), ('10s', 'ks', 'qs', '9c', 'jd'))
        self.assertTrue(hand.is_straight())
        self.assertTrue(hand.is_flush())
        self.assertTrue(hand.is_straight_flush())

    def testIsNotStraightFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10h', '9c'))
        self.assertFalse(hand.is_straight_flush())

    def testRoyalGreaterThanStraightFlush(self):
        board = ('qs', 'js', '10s', '8h', '4s')
        hand1 = FullHand(('as', 'ks'), board)
        hand2 = FullHand(('9s', '8s'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testStraightFlushGreaterThanQuads(self):
        hand1 = FullHand(('as', 'ks'), ('qs', 'js', '10s', 'kh', '6d'))
        hand2 = FullHand(('9s', '8s'), ('9d', '9h', '9c', 'kh', '6d'))

        self.assertHandGreaterThan(hand1, hand2)

    def testQuadsGreaterThanFullHouse(self):
        board = ('ks', 'kd', 'kh', '6s', '6c')
        hand1 = FullHand(('as', 'kc'), board)
        hand2 = FullHand(('9s', '9d'), board)

        self.assertTrue(hand1.is_quads())
        self.assertTrue(hand2.is_full_house())
        self.assertFalse(hand2.is_quads())
        self.assertHandGreaterThan(hand1, hand2)

    def testFullHouseGreaterThanFlush(self):
        board = ('ks', 'kd', 'kh', '3c', '5d')
        hand1 = FullHand(('9s', '9d'), board)
        hand2 = FullHand(('as', '9s'), ('7s', '4s', '2s', '8h', '6c'))
        
        self.assertHandGreaterThan(hand1, hand2)

    def testFlushGreaterThanStraight(self):
        board = ('6s', '4s', '2s', '9c', 'kh')
        hand1 = FullHand(('as', '9s'), board) 
        hand2 = FullHand(('3s', '5d'), board)
        
        self.assertHandGreaterThan(hand1, hand2)

    def testStraightGreaterThanTrips(self):
        board = ('6s', '4s', '2s', 'kh', 'jd')
        hand1 = FullHand(('3s', '5d'), board)
        hand2 = FullHand(('4h', '4d'), board) 
        
        self.assertHandGreaterThan(hand1, hand2)

    def testTripsGreaterThanTwoPair(self):
        board = ('6s', '4s', '2s', '3c', 'kh')
        hand1 = FullHand(('4h', '4d'), board) 
        hand2 = FullHand(('6d', '4h'), board)
        
        self.assertHandGreaterThan(hand1, hand2)

    def testTwoPairGreaterThanOnePair(self):
        board = ('6s', '4s', '2s', 'kh', 'jd')
        hand1 = FullHand(('6d', '4h'), board)
        hand2 = FullHand(('4h', '7d'), board) 
        
        self.assertHandGreaterThan(hand1, hand2)

    def testOnePairGreaterThanHighCard(self):
        board = ('6s', '4s', '2s', '3c', '8d')
        hand1 = FullHand(('4h', '7d'), board) 
        hand2 = FullHand(('7d', 'kh'), board)
        
        self.assertHandGreaterThan(hand1, hand2)

    def testBothOnePairHighestPairWins(self):
        board = ('6s', '4s', '2s', '3c', '8d')
        hand1 = FullHand(('kh', 'kd'), board)
        hand2 = FullHand(('qd', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothOnePairSamePairHighestSingleWins(self):
        # Same pair
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', 'jd'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same pair, same next highest
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', '9d'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same pair, same two next highest
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', '9d'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothDuplicateSingleHighestWins(self):
        # Same highest
        board = ('as', '5s', 'js', '10c', '9d')
        hand1 = FullHand(('qh', '4d'), board)
        hand2 = FullHand(('2d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same first two highest
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('jh', '4d'), board)
        hand2 = FullHand(('2d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same first three highest
        board = ('as', 'qs', '7s', '10c', '2d')
        hand1 = FullHand(('8h', '4d'), board)
        hand2 = FullHand(('5d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same first four highest
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('8h', '4d'), board)
        hand2 = FullHand(('5d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothTwoPairHighestPairWins(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('ah', '9d'), board)
        hand2 = FullHand(('qd', '9h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothTwoPairSameHighestPair(self):
        # Same highest pair
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('qh', '9d'), board)
        hand2 = FullHand(('qd', '7h'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same two pairs
        board = ('as', '3s', '9s', '10c', '9d')
        hand1 = FullHand(('ah', 'jc'), board)
        hand2 = FullHand(('ad', '8d'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothTripsHighestWins(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('ah', 'ad'), board)
        hand2 = FullHand(('qd', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothTripsSameTrips(self):
        # Same trips, first single wins
        board = ('as', 'ac', '7s', '10c', '9d')
        hand1 = FullHand(('ah', 'qd'), board)
        hand2 = FullHand(('ad', 'jh'), board)

        self.assertHandGreaterThan(hand1, hand2)

        # Same trips, same highest single
        board = ('as', 'ac', 'ks', '10c', '9d')
        hand1 = FullHand(('ah', 'qd'), board)
        hand2 = FullHand(('ad', 'jh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothStraightsHighestCardWins(self):
        board = ('ks', 'jc', '7s', '10c', '9d')
        hand1 = FullHand(('ah', 'qd'), board)
        hand2 = FullHand(('6d', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothStraightsAceLowLoses(self):
        board = ('2s', '3c', '4s', '5c', '8d')
        hand1 = FullHand(('kh', '6d'), board)
        hand2 = FullHand(('ad', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FullHandTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
