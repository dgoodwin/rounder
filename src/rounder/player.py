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

from logging import getLogger
logger = getLogger("rounder.player")

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
        self.cards = []
        
    def prompt(self, actions):
        """ 
        Prompt this player to make a choice among the given actions.
        """
        raise NotImplementedException()

    def __repr__(self):
        return "Player: " + self.name + " (chips: " + str(self.chips) + ")"



class CallingStation(Player):

    """ Player who will always continue to showdown if he has the option. """

    def __init__(self, name, chips=0):
        Player.__init__(self, name, chips)

        # List of preferred actions this player will try to respond to
        # in order. Sometimes overridden in tests.
        self.preferred_actions = [PostBlind]

    def prompt(self, actions):

        logger.debug("Prompting player: " + str(self))
        for a in actions:
            logger.debug("   " + str(a))

        for search_action in self.preferred_actions:
            action = self.__find_action(actions, search_action)
            if action is not None:
                # TODO: Supposed to be an asynchronous call here...
                logger.debug("Returning action: " + str(action))
                action.game.perform(action)
                return
        raise Exception("CallingStation couldn't find a suitable action: " +
            str(actions))

    def __find_action(self, action_list, action):
        for a in action_list:
            if isinstance(a, action):
                return a
        return None
