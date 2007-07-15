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

""" Tests for the rounder.serialize module. """

from logging import getLogger
logger = getLogger("rounder.test.serialize")

import unittest
import settestpath

from rounder.network.serialize import dumps, loads, register_message_classes
from rounder.dto import TableState

from tabletests import create_table

register_message_classes()

class CerealizerTests(unittest.TestCase):

    """ Tests exercising the rounder serialization code. """

    def test_simple_serialize(self):
        tuple = create_table(10, 0)
        table = tuple[1]
        state = TableState(table)
        str = dumps(state)

        new_state = loads(str)
        self.assertEquals(state.name, new_state.name)
        self.assertEquals(10, len(new_state.seats))



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CerealizerTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

