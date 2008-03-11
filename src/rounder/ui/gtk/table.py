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

        self.seat_buttons = []
        for i in range(0, 4):
            button_name = "seat%s-sit-button" % i
            button = self.glade_xml.get_widget(button_name)
            self.seat_buttons.append(button)

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

        self.table_window.show_all()

    def handle_sit_button(self, widget):
        seat = SEAT_BUTTON_INDEX[widget.get_name()]
        logger.info("Requesting seat %s" % seat)
        self.client_table.sit(seat)

    def sit_success_cb(self, seat):
        self.chat_line("You took seat %s." % seat)
        for button in self.seat_buttons:
            button.set_sensitive(False)

    def chat_line(self, msg):
        """ Append a line to the chat area on the table. """
        buf = self.chat_textview.get_buffer()
        buf.insert(buf.get_end_iter(), msg)


