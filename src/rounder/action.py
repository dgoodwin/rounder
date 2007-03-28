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

""" The Rounder Action Module """

class Action:

    """ 
    Parent Action class. Actions represent any decision a player 
    sitting at a table can be faced with.
    """

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def validate(self, params):
        """ 
        Validate an incoming action response to ensure the paramaters
        it contains are valid. This is done to ensure nobody can
        modify the source for their client and submit invalid
        responses.
        """
        pass



class PostBlind(Action):

    """ 
    Action a player can take to post a blind and take part in the
    next hand.
    """
    # Can double as an Ante?

    def __init__(self, game, player, amount):
        Action.__init__(self, game, player)
        self.amount = amount

    def __repr__(self):
        return "PostBlind: " + str(self.game.id) + " " + self.player.name + \
            " $" + str(self.amount)



class SitOut(Action):

    """ Action a player can take to sit out of the next hand. """

    def __init__(self, game, player):
        Action.__init__(self, game, player)

    def __repr__(self):
        return "SitOut: " + game.id + " " + player.name
