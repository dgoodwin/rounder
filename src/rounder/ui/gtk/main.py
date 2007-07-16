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

""" The Rounder GTK Client """

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade

import os
import sys

from logging import getLogger
logger = getLogger("rounder.ui.gtk.main")

def find_file_on_path(pathname):

    """
    Scan the Python path and locate a file with the given name.

    See:
      http://www.linuxjournal.com/xstatic/articles/lj/0087/4702/4702l2.html
    """

    if os.path.isabs(pathname):
        return pathname
    for dirname in sys.path:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return candidate
    raise Exception("Could not find %s on the Python path."
        % pathname)

class RounderGtk:

    """ The Rounder GTK Client """

    def __init__(self):

        logger.info("Starting application.")
        glade_file = 'rounder/ui/gtk/data/rounder.glade'
        glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        main_window = glade_xml.get_widget('main-window')

        signals = {
            'on_connect_activate': self.show_connect_dialog,
            'on_main_window_destroy' : self.shutdown,
        }
        glade_xml.signal_autoconnect(signals)

        main_window.show_all()

    def main(self):

        """ Launch the GTK main loop. """

        gtk.main()

    def show_connect_dialog(self, widget):
        
        """ Opens the connect to server dialog. """

        connect_dialog = ConnectDialog()

    def shutdown(self, widget):

        """ Closes the application. """

        logger.info("Stopping application.")
        gtk.main_quit()




class ConnectDialog:

    """ Dialog for connecting to a server. """

    def __init__(self):

        logger.debug("Opening connect dialog.")
        glade_file = 'rounder/ui/gtk/data/connect.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        connect_dialog = self.glade_xml.get_widget('connect-dialog')

        signals = {
            'on_connect_button_clicked': self.connect,
        }
        self.glade_xml.signal_autoconnect(signals)

        connect_dialog.show_all()

    def connect(self, widget):

        """ Attempt to open a connection to the host and port specified. """

        host_entry = self.glade_xml.get_widget('host-entry')
        host = host_entry.get_text()
        port_spinbutton = self.glade_xml.get_widget('port-spinbutton')
        port = port_spinbutton.get_value_as_int()
        logger.debug("Connecting to %s on port %s" % (host, port))

