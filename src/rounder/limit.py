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

""" The Rounder Limit Module """

class Limit:

    """ Parent class of all poker limits. """

    def __init__(self):
        pass



class FixedLimit(Limit):

    def __init__(self, small_bet, big_bet, small_blind=None, big_blind=None):
        Limit.__init__(self)
        self.small_bet = small_bet
        self.big_bet = big_bet

        self.small_blind = None
        if small_blind is not None:
            self.small_blind = small_blind
        else:
            self.small_blind = self.small_bet / 2

        if big_blind is not None:
            self.big_blind = big_blind
        else:
            self.big_blind = self.small_bet


