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

""" The Rounder Protocol Module """

from logging import getLogger
logger = getLogger("rounder.serialize")

import cerealizer
from rounder.dto import TableState, PlayerState
from rounder.card import Card
from rounder.currency import Currency
from rounder.action import PostBlind, Call, Raise, Fold
from rounder.limit import Limit, FixedLimit
from rounder.event import ALL_EVENTS

def register_message_classes():
    """ Registers all classes we'll be serializing with cerealizer. """
    l = [
        Card,
        TableState,
        Currency,
        PlayerState,
        PostBlind,
        Call,
        Raise,
        Fold,

        Limit, 
        FixedLimit,
    ]
    l.extend(ALL_EVENTS)

    for message_class in l:
        cerealizer.register(message_class)

def dumps(obj):
    """ Serialize the given object and return it's string form. """
    objstr = cerealizer.dumps(obj)
    return objstr

def loads(objstr):
    """ De-serialize the given string into it's original form. """
    obj = cerealizer.loads(objstr)
    return obj
