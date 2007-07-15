#!/usr/bin/env python

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

'''
Script to run all the pure rounder unit tests.

Everything here should run in-memory and extremely fast. (i.e. no file
system/database/network access)

Can also be run with testoob:

    testoob runtests.py suite

'''

import sys
# Adjust path so we can see the src modules running from branch as well
# as test dir:
sys.path.insert(0, './src/')
sys.path.insert(0, '../src/')
sys.path.insert(0, '../../src/')
sys.path.insert(0, './test/')
sys.path.insert(0, '../test/')

import unittest
import settestpath
import configureLogging

# Import all test modules here:
import cardtests
import decktests
import handtests
import pokerroomtests
import tabletests
import playertests
import gametests
import limittests
import actiontests
import pypokerevaltests
import serializetests
import network.servertests
import network.clienttests

from unittest import TestSuite

def suite():
    # Append all test suites here:
    return TestSuite((
        cardtests.suite(),
        decktests.suite(),
#        handtests.suite(), # defunct
        pokerroomtests.suite(),
        tabletests.suite(),
        playertests.suite(),
        gametests.suite(),
        limittests.suite(),
        actiontests.suite(),
        pypokerevaltests.suite(),
        serializetests.suite(),
        network.servertests.suite(),
        network.clienttests.suite(),
   ))

if __name__ == "__main__":
    try:
        import testoob
        testoob.main(defaultTest="suite")
    except ImportError:
        unittest.main(defaultTest="suite")
