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

""" Tests for the rounder.network.server module. """

from logging import getLogger
logger = getLogger("rounder.test.network.servertests")

import unittest

from server.servertests import BaseServerFixture
from rounder.event import *
from rounder.action import *

class EventTests(BaseServerFixture):

    def setUp(self):
        BaseServerFixture.setUp(self)

    def test_player_joined_events(self):
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(0, len(self.user2.events))
        self.user1_table.view_sit(self.user1, 0)
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))
        self.assertTrue(isinstance(self.user1.events[0], 
            PlayerJoinedGame))
        self.assertTrue(isinstance(self.user2.events[0], 
            PlayerJoinedGame))

    def test_new_hand_started(self):
        # TODO: Why does the user perspective still need a ref to the user?
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.clear_player_events()

        self.user1_table.view_start_game(self.user1)
        # No event until the blinds agree to post and the hand begins:
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(0, len(self.user2.events))

        # Post small blind:
        self.user1.act_randomly(self.table.id)
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(0, len(self.user2.events))

        # Post big blind, now we should see our event:
        self.user2.act_randomly(self.table.id)
        user1_events = filter_event_type(self.user1, NewHandStarted)
        self.assertEquals(1, len(user1_events))
        user2_events = filter_event_type(self.user1, NewHandStarted)
        self.assertEquals(1, len(user2_events))

    def test_player_posted_blind(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        self.user1.act_randomly(self.table.id)
        self.clear_player_events()
        self.user2.act_randomly(self.table.id)

        user1_events = filter_event_type(self.user1, PlayerPostedBlind)
        self.assertEquals(2, len(user1_events))
        user2_events = filter_event_type(self.user1, PlayerPostedBlind)
        self.assertEquals(2, len(user2_events))

    def test_hole_cards_dealt(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        self.user1.act_randomly(self.table.id)
        self.clear_player_events()
        self.user2.act_randomly(self.table.id)

        user1_events = filter_event_type(self.user1, HoleCardsDealt)
        self.assertEquals(1, len(user1_events))
        self.assertEquals(2, len(user1_events[0].cards))

        user2_events = filter_event_type(self.user2, HoleCardsDealt)
        self.assertEquals(1, len(user2_events))
        self.assertEquals(2, len(user1_events[0].cards))

    def test_community_cards_dealt(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)

        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)

        # Preflop action:
        self.user1.act(self.table.id, Call)
        self.clear_player_events()
        self.user2.act(self.table.id, Call)

        user1_events = filter_event_type(self.user1, CommunityCardsDealt)
        self.assertEquals(1, len(user1_events))
        self.assertEquals(3, len(user1_events[0].cards))

        user2_events = filter_event_type(self.user2, CommunityCardsDealt)
        self.assertEquals(1, len(user2_events))
        self.assertEquals(3, len(user2_events[0].cards))

    def test_player_sits_out_no_hand_underway(self):
        self.user1_table.view_sit(self.user1, 0)
        self.clear_player_events()

        self.user1_table.view_sit_out(self.user1)

        # Events should have gone out immediately:
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))

        self.assertTrue(isinstance(self.user1.events[0], 
            PlayerSatOut))
        self.assertTrue(isinstance(self.user2.events[0], 
            PlayerSatOut))




def filter_event_type(user, event_type):
    """ 
    Filter the users list of received events and return only those that 
    match the given type.
    """
    events_of_type = []
    for e in user.events:
        if isinstance(e, event_type):
            events_of_type.append(e)
    return events_of_type

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
