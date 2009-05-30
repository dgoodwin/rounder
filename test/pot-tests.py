#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2007 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006-2007 James Bowes <jbowes@dangerouslyinc.com>
#   Copyright (C) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
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

""" Tests for the Rounder pot module. """

from logging import getLogger
logger = getLogger("rounder.test.gametests")

import unittest

import settestpath

from rounder.currency import Currency
from rounder.pot import PotManager
from rounder.core import RounderException
from utils import create_players_list, create_players


class PotTests(unittest.TestCase):

    def setUp(self):
        self.players = create_players_list(10, 1000)

    def test_simple_pot(self):
        """ Test simple 2 player, 1 round pot. """
        potmgr = PotManager()
        potmgr.add({10: self.players[:2]})
        pots = potmgr.pots

        self.assertEquals(1, len(pots))
        self.assertEquals(2, len(pots[0].players))
        self.assertEquals(set(self.players[:2]), set(pots[0].players))
        self.assertEquals(20, pots[0].amount)

    def test_two_round_simple_pot(self):
        """ Test simple 2 player, 2 round pot. """
        potmgr = PotManager()
        potmgr.add({10: self.players[:2]})
        potmgr.add({10: self.players[:2]})
        pots = potmgr.pots

        self.assertEquals(1, len(pots))
        self.assertEquals(2, len(pots[0].players))
        self.assertEquals(set(self.players[:2]), set(pots[0].players))
        self.assertEquals(40, pots[0].amount)

    def test_one_allin(self):
        """ Test 2 player, one allin. """
        potmgr = PotManager()
        potmgr.add({10: self.players[:2]})
        self.players[0].allin = True
        potmgr.add({10: self.players[:2]})
        pots = potmgr.pots

        self.assertEquals(1, len(pots))
        self.assertEquals(2, len(pots[0].players))
        self.assertEquals(set(self.players[:2]), set(pots[0].players))
        self.assertEquals(40, pots[0].amount)

    def test_two_allin_split_pot(self):
        """ Test 2 players pushing in in different rounds. """
        potmgr = PotManager()
        self.players[2].allin = True
        potmgr.add({15: self.players[:3]})
        self.players[1].allin = True
        potmgr.add({10: self.players[:2]})
        pots = potmgr.pots

        self.assertEquals(2, len(pots))
        self.assertTrue(pots[1].is_main_pot)
        self.assertFalse(pots[0].is_main_pot)
        self.assertEquals(2, len(pots[0].players))
        self.assertEquals(3, len(pots[1].players))
        self.assertEquals(set(self.players[:2]), set(pots[0].players))
        self.assertEquals(set(self.players[:3]), set(pots[1].players))
        self.assertEquals(20, pots[0].amount)
        self.assertEquals(45, pots[1].amount)

    def test_two_allin_split_more_complicated(self):
        """ Test 2 players pushing in in different rounds, betting continues.

        Pots are:
           0 : 15 15 15
           1 : 16 16
           1 : 10 10
        """
        potmgr = PotManager()
        self.players[2].allin = True
        potmgr.add({15: [self.players[2]], 31: self.players[:2]})
        self.players[1].allin = True
        potmgr.add({10: self.players[:2]})
        pots = potmgr.pots

        self.assertEquals(2, len(pots))
        self.assertEquals(2, len(pots[0].players))
        self.assertEquals(3, len(pots[1].players))
        self.assertEquals(set(self.players[:2]), set(pots[0].players))
        self.assertEquals(set(self.players[:3]), set(pots[1].players))
        self.assertEquals((31 - 15) * 2 + 20, pots[0].amount)
        self.assertEquals(45, pots[1].amount)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PotTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
