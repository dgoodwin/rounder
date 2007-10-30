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

from rounder.core import RounderException
from rounder.currency import Currency

class ActionValidationException(RounderException):

    """ Exception thrown when invalid action parameters are received. """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



class Action:

    """ 
    Parent Action class. Actions represent any decision a player 
    sitting at a table can be faced with.
    """

    def __init__(self):
        pass

    def validate(self, params):
        """ 
        Validate an incoming action response to ensure the paramaters
        it contains are valid. This is done to ensure nobody can
        modify the source for their client and submit invalid
        responses.

        Parameters are expected to arrive as a list of strings. Actions
        can expect order and manipulate to other data types as they see
        fit.
        """
        pass

    @staticmethod
    def _check_params_length(params, expected_length):
        """ 
        Raise an ActionValidationException if the params list is not of the
        expected length.
        """
        if len(params) != expected_length:
            raise ActionValidationException(
                "Expected %s params but got %s" % (expected_length, 
                    len(params)))



class PostBlind(Action):

    """ 
    Action a player can take to post a blind and take part in the
    next hand.
    """
    # Can double as an Ante?

    def __init__(self, amount):
        Action.__init__(self)
        self.amount = amount

    def __repr__(self):
        return "PostBlind: " + " $" + str(self.amount)



class Call(Action):

    """ 
    Action a player can take to call the current bet.
    next hand.
    """

    def __init__(self, amount):
        Action.__init__(self)
        self.amount = amount

    def __repr__(self):
        return "Call: " + " $" + str(self.amount)



class Raise(Action):

    """ 
    Action a player can take to raise the current bet.
    
    The raise is specified by an amount over the current bet.
    """
    # TODO: Add existing bet to the contructor?

    def __init__(self, max_bet, min_bet):
        Action.__init__(self)
        self.max_bet = max_bet
        self.min_bet = min_bet
        # TODO: protect the amount better?
        self.amount = None # unknown until we receive a response from the player

    def __repr__(self):
        return "Raise ($%s - $%s): $%s" % (self.min_bet, self.max_bet, 
            self.amount)

    def validate(self, params):
        Action.validate(self, params)
        self._check_params_length(params, 1)
        amount = Currency(params[0])
        if amount < self.min_bet or amount > self.max_bet:
            raise ActionValidationException("Invalid raise amount: %s" 
                % (amount))
        self.amount = amount

class Fold(Action):

    """ 
    Action a player can take to fold the current hand.
    """

    def __init__(self):
        Action.__init__(self)

    def __repr__(self):
        return "Fold: "



