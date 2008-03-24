#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
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

""" Rounder Client - Everything needed for a UI. """

class Client:
    """ Everything you need to implement to be a client. """

    def __init__(self):
        pass

    def connect_success(self, client):
        """ Called when you are connected. """
        raise NotImplementedError

    # TODO: some type of error message?
    def connect_failure(self):
        """ Called when a connection fails. """
        raise NotImplementedError

    def list_tables_success(self, table_listings):
        """ 
        Called when you get a list of tables from the server. 
        
        table_listings - List of rounder.dto.TableListing objects.
        """
        raise NotImplementedError

    def list_tables_failure(self, tables):
        """ Called when you get a list of tables from the server. """
        raise NotImplementedError

    def open_table_success(self, client_table):
        """ 
        Table opened successfully. 

        client_table - Network client object specific to a particular table.
            See rounder.network.client.ClientTable.
        """
        raise NotImplementedError

    def log_error(self, failure):
        """ Called any time you want the client to log an error message. """
        return failure

class ClientTable:
    """ 
    Client UI representation of a table.

    Many server actions are specific to a particular table. Rather than
    return and send a table ID with every one of these requests we use an 
    object to encapsualte this info for us.
    """

    def __init__(self):
        pass

    def sit_success(self, seat_number):
        """ Called when seat successfully taken. """
        raise NotImplementedError

    def process_event(self, event):
        """ Called when an event arrives. """
        raise NotImplementedError

    def log_error(self, failure):
        """ 
        Called any time an error message is returned - will likely disappear.
        """
        return failure

    def prompt(self, actions):
        """ Prompt user to choose from the given actions. """
        raise NotImplementedError

