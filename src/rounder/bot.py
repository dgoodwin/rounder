#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2008 James Bowes <jbowes@dangerouslyinc.com>
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

import random

from logging import getLogger
logger = getLogger("rounder.ui.bot")

from rounder.ui.client import Client, ClientTable
from rounder.action import Raise
from rounder.network.client import RounderNetworkClient
from rounder.network.server import DEFAULT_SERVER_PORT


class RandomBot(Client):
    """ 
    An extremely stupid bot.

    Connects to the given server, opens the first table it can, takes an
    open seat, and proceeds to act completely randomly.
    """

    def __init__(self, host, port, username, password):

        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.client = RounderNetworkClient(self)
        self.client.connect(self.host, self.port, self.username, 
            self.password)

    def connect_success(self, perspective):
        logger.info("Connected to %s as %s." % (self.host, self.username))
        tables = self.client.get_table_list()

    def list_tables_success(self, table_listings):
        logger.debug("got list of tables:")

        # Attempt to open the first table:
        self.client.open_table(table_listings[0].id)

    def open_table_success(self, table_uplink):
        logger.debug("Opened table: %s" % table_uplink.table_id)
        client_table = RandomBotTable(table_uplink)
        table_uplink.ui = client_table
        # Find and take the first available seat:
        for i in range(10):
            if table_uplink.state.seats[i] == None:
                table_uplink.sit(i)
                break



class RandomBotTable(ClientTable):

    def __init__(self, table_uplink):
        self.table_uplink = table_uplink

    def sit_success(self, seat_num):
        pass

    def process_event(self, event):
        logger.info("Event: %s" % event)

    def prompt(self, actions):
        """ 
        Choose one of the actions in the given list, return it's index and any
        parameters required.
        """
        r = random.randint(0, len(actions) - 1)
        random_action = actions[r]
        params = []
        if isinstance(random_action, Raise):
            params.append(str(random_action.min_bet))
        self.table_uplink.act(r, params)

