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

""" The Rounder Player Module """

from rounder.core import NotImplementedException
from rounder.action import PostBlind

class Player:

    """ 
    Player at a poker table. Note one account could be playing at 
    multiple tables concurrently, in which case one Player would be
    created for each.
    """

    def __init__(self, name, chips=0):
        self.name = name
        self.chips = chips
        
    def prompt(self, game, actions):
        """ 
        Prompt this player to make a choice among the given actions.
        """
        raise NotImplementedException()



CALLING_STATION_PREFERRED_ACTIONS = [
    PostBlind,
]

class CallingStation(Player):

    """ Player who will always continue to showdown if he has the option. """

    def __init__(name, chips=0):
        Player.__init__(self, name, chips)

    def prompt(self, game, actions):
        for action in CALLING_STATION_PREFERRED_ACTIONS:
            if self.__action_is_present(actions, action):
                game.perform(user, action)
                return
        raise Exception("CallingStation couldn't find a suitable action: " +
            actions)

    def __action_is_present(self, action_list, action):
        for a in action_list:
            if type(a) == action:
                return True
        return False
