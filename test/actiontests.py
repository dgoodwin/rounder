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

""" Tests for the rounder.action module. """

import unittest

import settestpath

from rounder.action import Raise
from rounder.action import ActionValidationException
from rounder.player import Player

CHIPS = 1000

class RaiseTests(unittest.TestCase):

    def test_too_many_validation_params(self):
        p = Player(name="Player", chips=CHIPS)
        action = Raise(p, 2, 2)
        self.assertRaises(ActionValidationException, action.validate, 
            ["2", "lkl", "kkak"])

    def test_bogus_limit_raise(self):
        p = Player(name="Player", chips=CHIPS)
        action = Raise(p, 2, 2)
        self.assertRaises(ActionValidationException, action.validate,
            [3])

    def test_limit_raise(self):
        p = Player(name="Player", chips=CHIPS)
        action = Raise(p, 2, 2)
        self.assertEquals(None, action.amount)
        action.validate([2])
        self.assertEquals(2, action.amount)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RaiseTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
