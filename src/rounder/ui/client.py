#   Rounder - Poker for the GNOME Desktop
#
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
""" Rounder Client - Everything needed for a UI. """

class Client:
    """ Everything you need to implement to be a client. """

    def __init__(self):
        pass

    def connect_success(self, client):
        """ Called when you are connected. """
        pass

    # TODO: some type of error message?
    def connect_failure(self):
        """ Called when a connection fails. """
        pass

    def got_table_list(self, tables):
        """ Called when you get a list of tables from the server. """
        pass

    def log_error(self, failure):
        """ Called any time you want the client to log an error message. """
        return failure
