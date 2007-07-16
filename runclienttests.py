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

import sys
sys.path.insert(0, './src/')

from rounder.log import setup_logging
import logging
# Configure logging: (needs to be done before importing our modules)
log_conf_locations = ["./logging.conf"]
setup_logging(log_conf_locations)

from rounder.network.client import RounderNetworkClient
from rounder.network.server import SERVER_PORT
from rounder.network.serialize import register_message_classes

class TestClientUI:

    """ 
    Test UI implementation.
    """

    def __init__(self):

        self.client = RounderNetworkClient(self)
        self.client.connect('localhost', SERVER_PORT, "joe", "password")

    def connected(self):

        print "Connected!"
        tables = self.client.get_table_list()

    def got_table_list(self, tables):

        print "got list of tables:"
        for t in tables:
            print "   %s" % t[1]

        # Attempt to open the first table:
        self.client.open_table(tables[0][0])

    def table_opened(self, table_state):
        self.client.take_seat(table_state.id, 0)



if __name__ == '__main__':
    register_message_classes()
    ui = TestClientUI()

