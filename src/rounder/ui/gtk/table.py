#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
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

""" The Rounder GTK Table """

import gtk
import gtk.glade

from logging import getLogger
logger = getLogger("rounder.ui.gtk.table")

from rounder.ui.gtk.util import find_file_on_path
from rounder.ui.client import Table
from rounder.event import *
from rounder.action import *

SEAT_BUTTON_INDEX = {
    'seat0-sit-button': 0,
    'seat1-sit-button': 1,
    'seat2-sit-button': 2,
    'seat3-sit-button': 3,
    'seat4-sit-button': 4,
    'seat5-sit-button': 5,
    'seat6-sit-button': 6,
    'seat7-sit-button': 7,
    'seat8-sit-button': 8,
    'seat9-sit-button': 9,
}

class TableWindow(Table):
    """ Dialog for a poker table. """

    def __init__(self, app, client_table):
        """
        Create a new table window with a reference to the parent application
        window, as well as the client table we can use to perform actions.
        """

        logger.debug("Opening table window.")

        self.app = app
        self.client_table = client_table
        # TODO: Chicken and egg problem here, probably easy to solve:
        self.client_table.ui = self

        glade_file = 'rounder/ui/gtk/data/table.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        self.table_window = self.glade_xml.get_widget('table-window')
        self.table_window.set_title(client_table.state.name)

        table_name = self.glade_xml.get_widget('table-label')
        table_name.set_text(client_table.state.name)

        self.chat_textview = self.glade_xml.get_widget('chat-textview')

        limit = self.glade_xml.get_widget('limit-label')
        limit.set_text(str(client_table.state.limit))

        self.deal_button = self.glade_xml.get_widget('deal-button')
        self.deal_button.set_sensitive(False)

        self.call_button = self.glade_xml.get_widget('call-button')
        self.raise_button = self.glade_xml.get_widget('raise-button')
        self.fold_button = self.glade_xml.get_widget('fold-button')
        # Signal handlers we reuse:
        self.__call_handler_id = None
        self.__raise_handler_id = None
        self.__fold_handler_id = None
        self.__disable_action_buttons()


        self.gui_seats = []
        for i in range(0, 4):
            seat = GuiSeat(self.glade_xml, i)
            self.gui_seats.append(seat)
        # Will be a pointer to our GuiSeat:
        self.my_seat = None
        self.my_seat_num = None

        # Signal handling:
        # TODO: Replace these all with one signal?
        signals = {
            'on_seat0_sit_button_clicked': self.handle_sit_button,
            'on_seat1_sit_button_clicked': self.handle_sit_button,
            'on_seat2_sit_button_clicked': self.handle_sit_button,
            'on_seat3_sit_button_clicked': self.handle_sit_button,
            'on_seat4_sit_button_clicked': self.handle_sit_button,
            'on_seat5_sit_button_clicked': self.handle_sit_button,
            'on_seat6_sit_button_clicked': self.handle_sit_button,
            'on_seat7_sit_button_clicked': self.handle_sit_button,
            'on_seat8_sit_button_clicked': self.handle_sit_button,
            'on_seat9_sit_button_clicked': self.handle_sit_button,
            'on_deal_button_clicked': self.handle_deal_button,
        }
        self.glade_xml.signal_autoconnect(signals)
        self.table_window.connect("delete_event", self.confirm_window_close)

        # Render the initial table state:
        self.__render_table_state(self.client_table.state)

        # Clear these when a hand ends:
        self.my_hole_cards = None

        self.table_window.show_all()

    def confirm_window_close(self, widget, event, data=None):
        logger.debug("Confirming window close.")
        # NOTE: Just closing the window here for now, confirmation comes 
        # later:
        self.client_table.leave()
        return False # set to true for confirm screen

    def handle_sit_button(self, widget):
        seat = SEAT_BUTTON_INDEX[widget.get_name()]
        logger.info("Requesting seat %s" % seat)
        self.client_table.sit(seat)

    def handle_deal_button(self, widget):
        logger.info("Requesting to start a hand.")
        self.client_table.start_game()

    def sit_success(self, seat):
        self.my_seat = self.gui_seats[seat]
        self.my_seat_num = seat
        if not self.client_table.state.hand_underway:
            self.deal_button.set_sensitive(True)
        for seat in self.gui_seats:
            seat.sit_button_disable()

    def chat_line(self, msg):
        """ Append a line to the chat area on the table. """
        buf = self.chat_textview.get_buffer()
        buf.insert(buf.get_end_iter(), msg + "\n")
    
    def __disable_action_buttons(self):
        self.call_button.set_label("Call")
        self.call_button.set_sensitive(False)

        self.raise_button.set_label("Raise")
        self.raise_button.set_sensitive(False)

        self.fold_button.set_label("Fold")
        self.fold_button.set_sensitive(False)

    def handle_call_button(self, widget, data):
        """ Handle a call button press. """

        action_index = data[0]
        action = data[1]

        self.__disable_action_buttons()

        logger.debug("Calling $%s." % action.amount)
        self.client_table.act(action_index, [])

    def handle_raise_button(self, widget, data):
        """ Handle a raise button press. """

        action_index = data[0]
        action = data[1]
        raise_amount = data[2]

        self.__disable_action_buttons()

        logger.debug("Raising $%s." % raise_amount)
        self.client_table.act(action_index, [raise_amount])

    def handle_fold_button(self, widget, data):
        """ Handle a fold press. """

        action_index = data[0]
        action = data[1]

        self.__disable_action_buttons()

        logger.debug("Folding.")
        self.client_table.act(action_index, [])

    def prompt(self, actions):
        """ Prompt player to act. """
        index = 0
        logger.debug("Prompting with actions:")
        for action in actions:
            logger.debug("   %s" % action)
            if isinstance(action, PostBlind):
                self.call_button.set_label("Post blind: $%s" % action.amount)
                self.call_button.set_sensitive(True)
                if self.__call_handler_id != None:
                    self.call_button.disconnect(self.__call_handler_id)
                self.__call_handler_id = self.call_button.connect('clicked',
                        self.handle_call_button, (index, action))

            elif isinstance(action, Call):
                self.call_button.set_label("Call: $%s" % action.amount)
                self.call_button.set_sensitive(True)
                if self.__call_handler_id != None:
                    self.call_button.disconnect(self.__call_handler_id)
                self.__call_handler_id = self.call_button.connect('clicked', 
                        self.handle_call_button, (index, action))

            elif isinstance(action, Raise):
                # TODO: Note this is only for limit holdem currently:
                self.raise_button.set_label("Raise: $%s" % action.min_bet)
                self.raise_button.set_sensitive(True)
                if self.__raise_handler_id != None:
                    self.raise_button.disconnect(self.__raise_handler_id)
                self.__raise_handler_id = self.raise_button.connect('clicked', 
                        self.handle_raise_button, (index, action, 
                            action.min_bet))

            elif isinstance(action, Fold):
                self.fold_button.set_label("Fold")
                self.fold_button.set_sensitive(True)
                if self.__fold_handler_id != None:
                    self.fold_button.disconnect(self.__fold_handler_id)
                self.__fold_handler_id = self.fold_button.connect('clicked', 
                        self.handle_fold_button, (index, action)) 

            index = index + 1

    def process_event(self, event):
        """
        Display the incoming event to the user.

        Currently the event's all contain a table state DTO object which we
        can use to display the entire table. This obviously duplicates a lot
        of data and may have to change in the future to reduce bandwidth.
        For now we can get away with just using the table state to update
        everything at the table.
        """

        if isinstance(event, PlayerJoinedTable):
            self.chat_line("%s took seat %s." % (event.player_name, 
                    event.seat_num))
            if self.my_seat == None:
                self.gui_seats[event.seat_num].sit_button_disable()

        elif isinstance(event, PlayerPrompted):
            self.chat_line("Waiting for %s to act." % event.player_name)
            # If our deal button is enabled this is likely the initial
            # prompt to post blinds and we can disable the button as the
            # hand will soon be underway. If the server is unable to find
            # player's willing to post blinds a HandCancelled event will
            # be sent out.
            self.deal_button.set_sensitive(False)

        elif isinstance(event, HandCancelled):
            self.chat_line("Hand cancelled.")
            self.deal_button.set_sensitive(True)

        elif isinstance(event, NewHandStarted):
            self.chat_line("Dealing hand.")
            self.deal_button.set_sensitive(False)

        elif isinstance(event, PlayerPostedBlind):
            self.chat_line("%s posted blind: $%s" % (event.player_name,
                event.amount))

        elif isinstance(event, HoleCardsDealt):
            self.chat_line("Dealt hole cards: %s %s" % (event.cards[0], 
                event.cards[1]))
            self.my_hole_cards = event.cards

        self.__render_table_state(event.table_state)

    def __render_table_state(self, state):
        logger.debug("Rendering table state:")
        #state.print_state()
        for i in range(0, 4):
            seat = self.gui_seats[i]

            if state.seats[i] != None:
                player_state = state.seats[i]
                seat.set_username(player_state.name)
                seat.sit_button_disable()

                # Render cards:
                if player_state.folded:
                    seat.set_hole_cards("Folded")
                elif player_state.sitting_out:
                    seat.set_hole_cards("Sitting Out")
                elif player_state.num_cards == 0:
                    seat.set_hole_cards("")
                elif i == self.my_seat_num:
                    seat.show_hole_cards(self.my_hole_cards)
                else:
                    seat.set_hole_cards("XX XX")

            else:
                seat.set_username("")



class GuiSeat:
    """
    Tiny object to encapsulate hard coded assumptions about the widgets
    that compose a seat.
    """
    def __init__(self, glade_xml, seat_number):
        self.glade_xml = glade_xml
        self.seat_number = seat_number

        self.__player_label = self.glade_xml.get_widget("seat%s-player-label"
                % seat_number)

        button_name = "seat%s-sit-button" % seat_number
        self.__sit_button = self.glade_xml.get_widget(button_name)

        label_name = "seat%s-cards-label" % self.seat_number
        self.cards_label = self.glade_xml.get_widget(label_name)

    def set_username(self, username):
        self.__player_label.set_text(username)

    def sit_button_disable(self):
        self.__sit_button.set_sensitive(False)

    def show_hole_cards(self, cards):
        """
        Display hole cards.

        Cards will be set to None if we're displaying another player still
        in the hand. (done so we can visually see who's left and who's
        sitting out)
        """
        self.cards_label.set_text("%s %s" % (cards[0], cards[1]))

    def set_hole_cards(self, msg):
        """ Hole cards field also used to indicate status in the hand. """
        self.cards_label.set_text(msg)


