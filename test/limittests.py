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

""" Tests for the rounder.limit module. """

import unittest

import settestpath

from rounder.limit import FixedLimit
from rounder.currency import Currency

class FixedLimitTests(unittest.TestCase):

    def test_two_four(self):
        two_four = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        self.assertEqual(Currency(1), two_four.small_blind)
        self.assertEqual(Currency(2), two_four.big_blind)

    def test_micro_limits(self):
        limit = FixedLimit(small_bet=Currency(0.10), big_bet=Currency(0.20))
        self.assertEqual(Currency(0.05), limit.small_blind)
        self.assertEqual(Currency(0.10), limit.big_blind)

    def test_one_two(self):
        limit = FixedLimit(small_bet=Currency(1), big_bet=Currency(2))
        self.assertEqual(Currency(0.5), limit.small_blind)
        self.assertEqual(Currency(1), limit.big_blind)

    def test_rounding(self):
        limit = FixedLimit(small_bet=Currency(0.25), big_bet=Currency(0.5))
        self.assertEqual(Currency(0.12), limit.small_blind)
        self.assertEqual(Currency(0.25), limit.big_blind)

    def test_custom_blinds(self):
        limit = FixedLimit(small_bet=Currency(0.25), big_bet=Currency(0.5),
            small_blind=Currency(0.10), big_blind=Currency(0.25))
        self.assertEqual(Currency(0.10), limit.small_blind)
        self.assertEqual(Currency(0.25), limit.big_blind)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FixedLimitTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

