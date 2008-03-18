
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







def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FullHandTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
