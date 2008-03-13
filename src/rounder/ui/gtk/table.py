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

class TableWindow:
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


        self.gui_seats = []
        for i in range(0, 4):
            seat = GuiSeat(self.glade_xml, i)
            self.gui_seats.append(seat)

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
        }
        self.glade_xml.signal_autoconnect(signals)

        self.table_window.connect("delete_event", self.confirm_window_close)

        self.__render_table_state(self.client_table.state)

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

    def sit_success_cb(self, seat):
        self.chat_line("You took seat %s." % seat)
        for seat in self.gui_seats:
            seat.sit_button_disable()

    def chat_line(self, msg):
        """ Append a line to the chat area on the table. """
        buf = self.chat_textview.get_buffer()
        buf.insert(buf.get_end_iter(), msg)
    
    def process_event(self, event):
        """
        Display the incoming event to the user.

        Currently the event's all contain a table state DTO object which we
        can use to display the entire table. This obviously duplicates a lot
        of data and may have to change in the future to reduce bandwidth.
        For now we can get away with just using the table state to update
        everything at the table.
        """
        self.__render_table_state(event.table_state)

    def __render_table_state(self, state):
        logger.debug("Rendering table state:")
        state.print_state()
        for i in range(0, 4):
            if state.seats[i] != None:
                self.gui_seats[i].set_username(state.seats[i].name)
            else:
                self.gui_seats[i].set_username("")



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

    def set_username(self, username):
        self.__player_label.set_text(username)

    def sit_button_disable(self):
        self.__sit_button.set_sensitive(False)

