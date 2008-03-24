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

""" Rounder Utilities """

from optparse import OptionParser

def find_action_in_list(action, action_list):
    for a in action_list:
        if isinstance(a, action):
            return a
    return None

def build_cli_option_parser():
    """ 
    Build an option parser with the options frequently requested from
    the command line scripts.
    """
    parser = OptionParser()
    parser.add_option("--host", dest="host", help="host to connect to")
    parser.add_option("--port", dest="port", type="int",
        help="port the rounder server is running on (default: 35100)")
    parser.add_option("-u", "--username", dest="username",
        help="username to play as")
    parser.add_option("-p", "--password", dest="password",
        help="server password")

    return parser

