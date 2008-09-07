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

from rounder.limit import FixedLimit, NoLimit
from rounder.currency import Currency
from rounder.utils import find_action_in_list
from rounder.player import Player
from rounder.action import Call, Raise, Fold

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

    def test_actions(self):
        two_four = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        p = Player('Some Player', chips=1000)
        actions = two_four.create_actions(p, 0, 1, 1)
        self.assertEquals(3, len(actions))

        call = find_action_in_list(Call, actions)
        self.assertTrue(call != None)
        self.assertEquals(1, call.amount)

        r = find_action_in_list(Raise, actions)
        self.assertTrue(r != None)
        self.assertEquals(2, r.min_bet)
        self.assertEquals(2, r.max_bet)

    def test_actions_raise_all_in(self):
        two_four = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        p = Player('Some Player', chips=3.5)
        actions = two_four.create_actions(p, 0, 2, 1)
        self.assertEquals(3, len(actions))

        # Should detect that we don't have enough to make the full raise and
        # adjust the raise limits accordingly:
        r = find_action_in_list(Raise, actions)
        self.assertTrue(r != None)
        self.assertEquals(1.5, r.min_bet)
        self.assertEquals(1.5, r.max_bet)

    def test_actions_call_all_in(self):
        two_four = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        p = Player('Some Player', chips=1.5)
        actions = two_four.create_actions(p, 0, 2, 1)
        self.assertEquals(2, len(actions))

        # Should detect that we don't have enough to call and
        # adjust the call amount accordingly:
        c = find_action_in_list(Call, actions)
        self.assertTrue(c != None)
        self.assertEquals(1.5, c.amount)

    def test_actions_previous_player_raised_all_in(self):
        # Test that if a player raises all in, the following player will
        # be able to call the exact amount raised, but a raise would complete
        # the partial raise the all-in player couldn't.
        two_four = FixedLimit(small_bet=Currency(2), big_bet=Currency(4))
        p = Player('Some Player', chips=1000)
        actions = two_four.create_actions(p, 0, 3.5, 1)
        self.assertEquals(3, len(actions))

        c = find_action_in_list(Call, actions)
        self.assertTrue(c != None)
        self.assertEquals(3.5, c.amount)

        r = find_action_in_list(Raise, actions)
        self.assertTrue(r != None)
        self.assertEqual(0.5, r.max_bet)
        self.assertEqual(0.5, r.min_bet)
        


class NoLimitTests(unittest.TestCase):

    def test_creation(self):
        nl = NoLimit(small_blind=Currency(0.5), big_blind=Currency(1))
        self.assertEquals("$0.50/1.00 no-limit", str(nl))

    def test_normal_actions(self):
        # Test the normal situation where a player has enough chips to cover
        # the minimum raise and then some:
        nl = NoLimit(small_blind=Currency(0.5), big_blind=Currency(1))
        p = Player('Some Player', chips=1000)
        actions = nl.create_actions(p, 0, Currency(100), 0)
        self.assertEquals(3, len(actions))
        c = find_action_in_list(Call, actions)
        r = find_action_in_list(Raise, actions)
        self.assertEquals(Currency(100), c.amount)
        print r
        print r.min_bet
        self.assertEquals(Currency(100), r.min_bet)
        self.assertNone(r.max_bet)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FixedLimitTests))
    suite.addTest(unittest.makeSuite(NoLimitTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

