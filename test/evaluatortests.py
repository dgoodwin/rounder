
import unittest

import settestpath

from rounder.evaluator import FullHand


class FullHandTest(unittest.TestCase):

    def assertHandGreaterThan(self, hand1, hand2):
        if not hand1 > hand2:
            self.fail("0x%.6X not greater than 0x%.6X" %
                    (hand1._relative_value, hand2._relative_value))

    def assertHandEquals(self, hand1, hand2):
        if not hand1 == hand2:
            self.fail("0x%.6X not equal to 0x%.6X" %
                    (hand1._relative_value, hand2._relative_value))


class RoyalTests(FullHandTest):

    def testIsRoyal(self):
        hand = FullHand(('ad', 'kd'), ('qd', 'jd', '10d', '10s', '7h'))
        self.assertTrue(hand.is_royal())

    def testIsStraightFlushButNotRoyal(self):
        hand = FullHand(('as', '6d'), ('5d', '4d', '3d', '2d'))
        self.assertFalse(hand.is_royal())

    def testIsRoyalNotRoyal(self):
        hand = FullHand(('as', 'kd'), ('qd', 'jd', '10d', '10s', '7h'))
        self.assertFalse(hand.is_royal())


class FlushTests(FullHandTest):

    def testIsFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'js', '4s', '6c', 'jd'))
        self.assertTrue(hand.is_flush())

    def testIsNotFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6c', '8h'))
        self.assertFalse(hand.is_flush())

    def testSameHighCard(self):
        board = ('as', '4s', 'qs', '3c', '9s')
        hand1 = FullHand(('ks', '2s'), board)
        hand2 = FullHand(('jd', '6s'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameTwoHighCards(self):
        board = ('as', '4s', 'qs', '3c', '9s')
        hand1 = FullHand(('10s', '2s'), board)
        hand2 = FullHand(('jd', '6s'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameHighCardOneHandWithHighOfAnotherSuit(self):
        board = ('as', '4s', 'js', '3c', '9s')
        hand1 = FullHand(('qs', '6s'), board)
        hand2 = FullHand(('kd', '2s'), board)

        self.assertHandGreaterThan(hand1, hand2)


class OnePairTests(FullHandTest):

    def testIsOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'ad', '4s', '6h', '8c'))
        self.assertTrue(hand.is_one_pair())

    def testIsNotOnePair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6h', '8c'))
        self.assertFalse(hand.is_one_pair())

    def testBothOnePairHighestPairWins(self):
        board = ('6s', '4s', '2s', '3c', '8d')
        hand1 = FullHand(('kh', 'kd'), board)
        hand2 = FullHand(('qd', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothOnePairSamePairHighestSingleWins(self):
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', 'jd'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSamePairSameNextHighest(self):
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', '9d'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSamePairSameTwoNextHighest(self):
        board = ('ks', '4s', '2s', '3c', '10d')
        hand1 = FullHand(('kh', '9d'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)


class FullHouseTests(FullHandTest):

    def testIsFullHouse(self):
        hand = FullHand(('as', 'ks'), ('kd', 'ad', 'ac', '10d', '9s'))
        self.assertTrue(hand.is_full_house())

    def testIsNotFullHouse(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '9s'))
        self.assertFalse(hand.is_full_house())

    def testBothFullHouseBestTripsWins(self):
        board = ('8s', 'ks', '9s', '9c', '8d')
        hand1 = FullHand(('kh', '9d'), board)
        hand2 = FullHand(('kd', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothFullHouseSameTrips(self):
        board = ('8s', '9s', '9s', '9c', '6d')
        hand1 = FullHand(('kh', 'kd'), board)
        hand2 = FullHand(('7d', '7h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothFullHouseTwoTrips(self):
        board = ('as', 'th', 'tc', '2c', '2d')
        hand1 = FullHand(('7d', 'ts'), board)
        hand2 = FullHand(('2h', 'td'), board)

        self.assertHandEquals(hand1, hand2)


class QuadsTests(FullHandTest):

    def testIsQuads(self):
        hand = FullHand(('as', 'ks'), ('ad', 'ac', 'ah', '10d', '9s'))
        self.assertTrue(hand.is_quads())

    def testIsNotQuads(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '8c'))
        self.assertFalse(hand.is_quads())

        hand = FullHand(('9c', '9s'), ('qs', 'qd', 'qh', '10d', '8c'))
        self.assertFalse(hand.is_quads())

    def testBothQuadsHighestWins(self):
        board = ('as', 'qs', 'ac', '10c', 'qc')
        hand1 = FullHand(('ah', 'ad'), board)
        hand2 = FullHand(('qd', 'qh'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothQuadsSameTrips(self):
        # Same trips, first single wins
        board = ('as', 'ac', 'ad', 'ah', '9d')
        hand1 = FullHand(('kh', 'qd'), board)
        hand2 = FullHand(('8d', 'jh'), board)

        self.assertHandGreaterThan(hand1, hand2)


class TwoPairTests(FullHandTest):

    def testIsTwoPair(self):
        hand = FullHand(('as', 'ks'), ('ad', 'kc', '9h', 'jd', '5c'))
        self.assertTrue(hand.is_two_pair())

    def testIsNotTwoPair(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '6s', '7h'))
        self.assertFalse(hand.is_two_pair())

    def testBothTwoPairHighestPairWins(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('ah', '9d'), board)
        hand2 = FullHand(('qd', '9h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testBothTwoPairSameHighestPair(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('qh', '9d'), board)
        hand2 = FullHand(('qd', '7h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameTwoPairs(self):
        board = ('as', '3s', '9s', '10c', '9d')
        hand1 = FullHand(('ah', 'jc'), board)
        hand2 = FullHand(('ad', '8d'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testThreePairsUseThirdForSingle(self):
        board  = ('7h', 'jc', '9s', 'td', 'jh')
        hand1 = FullHand(('tc', '9h'), board)
        hand2 = FullHand(('5d', 'th'), board)

        self.assertHandEquals(hand1, hand2)

    def testThreePairsDontUseThirdForSingle(self):
        board  = ('2h', 'jc', '2s', 'td', 'jh')
        hand1 = FullHand(('tc', '9h'), board)
        hand2 = FullHand(('5d', 'th'), board)

        self.assertHandGreaterThan(hand1, hand2)



class TripsTests(FullHandTest):

    def testIsTrips(self):
        hand = FullHand(('as', 'js'), ('ad', 'kc', 'ac', '10d', '9s'))
        self.assertTrue(hand.is_trips())

    def testIsNotTrips(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10d', '8s'))
        self.assertFalse(hand.is_trips())

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

    def testSameTripsSameHighestSingle(self):
        board = ('as', 'ac', 'ks', '10c', '9d')
        hand1 = FullHand(('ah', 'qd'), board)
        hand2 = FullHand(('ad', 'jh'), board)

        self.assertHandGreaterThan(hand1, hand2)


class StraightTests(FullHandTest):

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

    def testIsStraightAceHighAndDeuce(self):
        hand = FullHand(['2d', 'kd'], ['qd', 'as', 'th', '4d', 'js'])
        self.assertTrue(hand.is_straight())

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

    def testBothStraightNonContiguousHighCard(self):
        board = ['7c', '5d', '9d', '8c', '5h']
        hand1 = FullHand(['ts', '6h'], board)
        hand2 = FullHand(['jd', '6s'], board)

        self.assertHandGreaterThan(hand1, hand2)


class StraightFlushTests(FullHandTest):

    def testIsStraightFlush(self):
        hand = FullHand(('9s', 'js'), ('10s', 'ks', 'qs', '9c', 'jd'))
        self.assertTrue(hand.is_straight())
        self.assertTrue(hand.is_flush())
        self.assertTrue(hand.is_straight_flush())

    def testComplicatedIsStraightFlush(self):
        # Possible to have cards that compose a flush and a straight, but not
        # a straight flush:
        hand = FullHand(('9s', '10c'), ('js', 'qs', 'ks', '5d', '2s'))
        self.assertTrue(hand.is_straight())
        self.assertTrue(hand.is_flush())
        self.assertFalse(hand.is_straight_flush())

    def testIsNotStraightFlush(self):
        hand = FullHand(('as', '9s'), ('qs', 'jd', '4s', '10h', '9c'))
        self.assertFalse(hand.is_straight_flush())

    def testRoyalGreaterThanStraightFlush(self):
        board = ('qs', 'js', '10s', '8h', '4s')
        hand1 = FullHand(('as', 'ks'), board)
        hand2 = FullHand(('9s', '8s'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testLowStraightFlush(self):
        hand = FullHand(('as', '6d'), ('5d', '4d', '3d', '2d'))
        self.assertTrue(hand.is_straight_flush())

def testBothStraightsFlushHighestCardWins(self):
        board = ('6h', 'jh', 'qh', '10h', '9h')
        hand1 = FullHand(('kh', 'qd'), board)
        hand2 = FullHand(('6d', '8h'), board)

        self.assertHandGreaterThan(hand1, hand2)


class SinglesTests(FullHandTest):

    def testBothDuplicateSingleHighestWins(self):
        # Same highest
        board = ('as', '5s', 'js', '10c', '9d')
        hand1 = FullHand(('qh', '4d'), board)
        hand2 = FullHand(('2d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameFirstTwoHighest(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('jh', '4d'), board)
        hand2 = FullHand(('2d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameFirstThreeHighest(self):
        board = ('as', 'qs', '7s', '10c', '2d')
        hand1 = FullHand(('8h', '4d'), board)
        hand2 = FullHand(('5d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)

    def testSameFirstFourHighest(self):
        board = ('as', 'qs', '7s', '10c', '9d')
        hand1 = FullHand(('8h', '4d'), board)
        hand2 = FullHand(('5d', '3h'), board)

        self.assertHandGreaterThan(hand1, hand2)


class HandClassComparisonTests(FullHandTest):

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

class FullHandReprTests(unittest.TestCase):

    def testRoyal(self):
        hand = FullHand(('qs', 'ts'), ('as', 'js', 'ks', '9s', '5d'))
        self.assertEquals("a royal flush (AKQJT)", str(hand))

    def testStraightFlush(self):
        hand = FullHand(('qs', 'ts'), ('3s', 'js', 'ks', '9s', '5d'))
        self.assertEquals("a straight flush (KQJT9)", str(hand))

    def testQuads(self):
        hand = FullHand(('qs', 'qd'), ('qh', 'qc', 'ks', '9s', '5d'))
        self.assertEquals("quads (QQQQK)", str(hand))

    def testFullHouse(self):
        hand = FullHand(('qs', 'qd'), ('qh', 'kc', 'ks', '9s', '5d'))
        self.assertEquals("a full house (QQQKK)", str(hand))

    def testFlush(self):
        hand = FullHand(('qs', 'qd'), ('8s', 'kc', 'ks', '9s', '2s'))
        self.assertEquals("a flush (KQ982)", str(hand))

    def testStraight(self):
        hand = FullHand(('jh', 'qd'), ('th', 'kc', 'ks', '9s', '2s'))
        self.assertEquals("a straight (KQJT9)", str(hand))

    def testTrips(self):
        hand = FullHand(('kh', '3d'), ('th', 'kc', 'ks', '9s', '2s'))
        self.assertEquals("trips (KKKT9)", str(hand))

    def testTwoPair(self):
        hand = FullHand(('qh', 'qd'), ('7h', 'kc', 'ks', '5s', '2s'))
        self.assertEquals("two pair (KKQQ7)", str(hand))

    def testOnePair(self):
        hand = FullHand(('jh', 'qd'), ('qh', 'tc', '6s', '4s', '2s'))
        self.assertEquals("one pair (QQJT6)", str(hand))

    def testHighCard(self):
        hand = FullHand(('ah', 'qd'), ('th', '2c', '6s', '3s', '7s'))
        self.assertEquals("a high card (AQT76)", str(hand))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RoyalTests))
    suite.addTest(unittest.makeSuite(StraightFlushTests))
    suite.addTest(unittest.makeSuite(QuadsTests))
    suite.addTest(unittest.makeSuite(StraightTests))
    suite.addTest(unittest.makeSuite(FlushTests))
    suite.addTest(unittest.makeSuite(FullHouseTests))
    suite.addTest(unittest.makeSuite(TripsTests))
    suite.addTest(unittest.makeSuite(TwoPairTests))
    suite.addTest(unittest.makeSuite(OnePairTests))
    suite.addTest(unittest.makeSuite(SinglesTests))
    suite.addTest(unittest.makeSuite(HandClassComparisonTests))
    suite.addTest(unittest.makeSuite(FullHandReprTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
