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
            PlayerJoinedTable))
        self.assertTrue(isinstance(self.user2.events[0],
            PlayerJoinedTable))

    def test_player_left_events(self):
        self.user1_table.view_sit(self.user1, 0)
        self.clear_player_events()
        self.user1_table.view_leave(self.user1)

        user2_events = filter_event_type(self.user2, PlayerLeftTable)

        self.assertEquals(1, len(user2_events))

        self.assertTrue(isinstance(user2_events[0],
            PlayerLeftTable))

    def test_new_hand_started(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.clear_player_events()

        self.user1_table.view_start_game(self.user1)
        # No event until the blinds agree to post and the hand begins:
        # Should first get a PlayerPrompted event (gathering blinds):
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))
        self.assertTrue(isinstance(self.user1.events[0], PlayerPrompted))
        self.assertTrue(isinstance(self.user2.events[0], PlayerPrompted))

        # Post small blind:
        self.user1.act_randomly(self.table.id)

        # Post big blind, now we should see our event:
        self.user2.act_randomly(self.table.id)
        user1_events = filter_event_type(self.user1, NewHandStarted)
        self.assertEquals(1, len(user1_events))
        user2_events = filter_event_type(self.user1, NewHandStarted)
        self.assertEquals(1, len(user2_events))

    def test_hand_cancelled(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.clear_player_events()

        self.user1_table.view_start_game(self.user1)
        # No event until the blinds agree to post and the hand begins:
        # Should first get a PlayerPrompted event (gathering blinds):
        self.assertEquals(1, len(self.user1.events))
        self.assertEquals(1, len(self.user2.events))
        self.assertTrue(isinstance(self.user1.events[0], PlayerPrompted))
        self.assertTrue(isinstance(self.user2.events[0], PlayerPrompted))
        self.clear_player_events()

        # Player we're waiting on leaves the table:
        self.user1_table.view_leave(self.user1)
        self.assertEquals(0, len(self.user1.events))
        self.assertEquals(2, len(self.user2.events))
        print self.user2.events
        self.assertTrue(isinstance(self.user2.events[0], PlayerLeftTable))
        self.assertTrue(isinstance(self.user2.events[1], HandCancelled))

    def test_player_posted_blind(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        self.user1.act_randomly(self.table.id)
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

    def test_player_sits_out_during_hand(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)

        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)

        # User 2 sits out, but the hand is already underway and they're
        # second to act, therefore the PlayerSatOut event shouldn't be
        # sent until after the hand is completed:
        self.user2_table.view_sit_out(self.user2)

        self.assertEquals(0, len(filter_event_type(self.user1, PlayerSatOut)))
        self.assertEquals(0, len(filter_event_type(self.user2, PlayerSatOut)))

        self.user1.act(self.table.id, Fold)
        # TODO: Check that user 2 wins once event is written:
        self.assertEquals(1, len(filter_event_type(self.user1, PlayerSatOut)))
        self.assertEquals(1, len(filter_event_type(self.user2, PlayerSatOut)))

    def test_player_called(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)
        # Preflop action:
        self.user1.act(self.table.id, Call)
        self.user2.act(self.table.id, Call)

        user1_events = filter_event_type(self.user1, PlayerCalled)
        self.assertEquals(2, len(user1_events))
        user1_call = user1_events[0]
        self.assertEquals(self.user1.username, user1_call.username)
        self.assertEquals(Currency(1), user1_call.amount)
        user2_call = user1_events[1]
        self.assertEquals(self.user2.username, user2_call.username)
        self.assertEquals(Currency(0), user2_call.amount)

        user2_events = filter_event_type(self.user2, PlayerCalled)
        self.assertEquals(2, len(user2_events))
        user1_call = user2_events[0]
        self.assertEquals(self.user1.username, user1_call.username)
        self.assertEquals(Currency(1), user1_call.amount)
        user2_call = user2_events[1]
        self.assertEquals(self.user2.username, user2_call.username)
        self.assertEquals(Currency(0), user2_call.amount)

    def test_player_raised(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)
        # Preflop action:
        self.user1.act(self.table.id, Call)
        self.user2.act(self.table.id, Raise, [2])

        user1_events = filter_event_type(self.user1, PlayerRaised)
        self.assertEquals(1, len(user1_events))
        user2_raise = user1_events[0]
        self.assertEquals(self.user2.username, user2_raise.username)
        self.assertEquals(Currency(2), user2_raise.amount)

        user2_events = filter_event_type(self.user2, PlayerRaised)
        self.assertEquals(1, len(user2_events))
        user2_raise = user2_events[0]
        self.assertEquals(self.user2.username, user2_raise.username)
        self.assertEquals(Currency(2), user2_raise.amount)

    def test_player_folded(self):
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)
        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)
        # Preflop action:
        self.user1.act(self.table.id, Call)
        self.user2.act(self.table.id, Fold)

        user1_events = filter_event_type(self.user1, PlayerFolded)
        self.assertEquals(1, len(user1_events))
        user2_fold = user1_events[0]
        self.assertEquals(self.user2.username, user2_fold.username)

        user2_events = filter_event_type(self.user2, PlayerFolded)
        self.assertEquals(1, len(user2_events))
        user2_fold = user2_events[0]
        self.assertEquals(self.user2.username, user2_fold.username)

    def __run_complete_hand(self):
        """
        Run through a complete hand checking down the action.
        """
        self.user1_table.view_sit(self.user1, 0)
        self.user2_table.view_sit(self.user2, 1)
        self.user1_table.view_start_game(self.user1)

        # Post blinds:
        self.user1.act_randomly(self.table.id)
        self.user2.act_randomly(self.table.id)

        # Preflop action:
        self.user1.act(self.table.id, Call) 
        self.user2.act(self.table.id, Call) # more like a check

        # Flop action:
        self.user2.act(self.table.id, Call) # more like a check
        self.user1.act(self.table.id, Call) # more like a check

        # Turn action:
        self.user2.act(self.table.id, Call) # more like a check
        self.user1.act(self.table.id, Call) # more like a check

        # River action:
        self.user2.act(self.table.id, Call) # more like a check
        self.user1.act(self.table.id, Call) # more like a check


    def test_game_ending(self):
        self.__run_complete_hand()
        gameover_events = filter_event_type(self.user1, GameEnding)
        self.assertEquals(1, len(gameover_events))
        gameover_events = filter_event_type(self.user2, GameEnding)
        self.assertEquals(1, len(gameover_events))

    def test_player_showed_cards(self):
        self.__run_complete_hand()
        events = filter_event_type(self.user1, PlayerShowedCards)
        self.assertEquals(2, len(events))
        events = filter_event_type(self.user2, PlayerShowedCards)
        self.assertEquals(2, len(events))

    def test_game_over(self):
        self.__run_complete_hand()
        events = filter_event_type(self.user1, GameOver)
        self.assertEquals(1, len(events))
        events = filter_event_type(self.user2, GameOver)
        self.assertEquals(1, len(events))



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
