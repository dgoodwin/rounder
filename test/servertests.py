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

""" Tests for the rounder.server module. """

import unittest

import settestpath
import rounder.server
import rounder.client

class RounderServerTests(unittest.TestCase):

    def test_something(self):
        pass
        #rounder.server.main()
        #rounder.client.main()



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RounderServerTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
