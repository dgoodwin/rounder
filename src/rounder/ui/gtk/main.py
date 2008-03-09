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
from twisted.internet import gtk2reactor
gtk2reactor.install()

from rounder.network.client import RounderNetworkClient
from rounder.network.serialize import register_message_classes

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
    """ 
    The Rounder GTK Client 

    Represents the main Rounder interface to connect to a server, view
    available tables, and join them. (opening a separate window)
    """

    def __init__(self):

        logger.info("Starting application.")
        register_message_classes()

        glade_file = 'rounder/ui/gtk/data/rounder.glade'
        glade_xml = gtk.glade.XML(find_file_on_path(glade_file))

        main_window = glade_xml.get_widget('main-window')
        self.table_list = glade_xml.get_widget('table-list')
        self.statusbar = glade_xml.get_widget('statusbar')

        signals = {
            'on_connect_activate': self.show_connect_dialog,
            'on_main_window_destroy' : self.shutdown,
            'on_connect_button_clicked': self.show_connect_dialog,
            'on_quit_button_clicked': self.shutdown,
            'on_table_list_row_activated': self.open_table,
        }
        glade_xml.signal_autoconnect(signals)

        treeselection = self.table_list.get_selection()
        treeselection.set_mode(gtk.SELECTION_SINGLE)

        # Reference to a network client.
        self.client = None

        self.connect_dialog = None # Set once connect dialog is open

        self.set_status("Connect to a server to begin playing.")

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def shutdown(self, widget):
        """ Closes the application. """
        if self.client != None:
            self.client.shutdown()
        logger.info("Stopping application.")
        gtk.main_quit()

    def open_table(self, treeview, row, column):
        """ 
        Open a table window.

        Connected to the table list and called when the user selected a table
        to join.
        """
        logger.info("Opening table window")

        model = treeview.get_model()
        logger.debug("   row clicked: %s" % row)
        logger.debug("   table id: %s" % model[row][0])
        logger.debug("   table name: %s" % model[row][1])

        table_win = TableWindow(self)

    def show_connect_dialog(self, widget):
        """ Opens the connect to server dialog. """
        if self.connect_dialog == None:
            self.connect_dialog = ConnectDialog(self)
        else:
            logger.debug("Connect dialog already open.")

    def connect_success_cb(self, client):
        """ 
        Callback used by the connect dialog after a connection to a server
        has been successfully made.
        """
        logger.info("Connected to %s:%s as %s" % (client.host, client.port, 
            client.username))
        self.client = client
        self.connect_dialog.destroy()
        self.connect_dialog = None
        self.set_status("Connected!")
        self.client.get_table_list()

    def connect_failure_cb(self):
        """ Connection failed callback. """
        logger.warn("Connect failed")
        self.connect_dialog.set_status("Login failed.")

    def got_table_list(self, table_listings):
        """ 
        Populate the list of tables in the main server window. 

        GTK TreeView's aren't fun but this works in conjunction with the
        __cell_* methods to populate the columns.
        """

        logger.debug("Populating table list")
        column_names = ["Table ID", "Name", "Limit", "Players"]
        cell_data_funcs = [self.__cell_table_id, self.__cell_table, 
            self.__cell_limit, self.__cell_players]

        tables = gtk.ListStore(int, str, str, str)
        for table in table_listings:
            tables.append([table.id, table.name, table.limit, 
                table.player_count])

        columns = [None] * len(column_names)

        # Populate the table columns and cells:
        for n in range (0, len(column_names)):
            cell = gtk.CellRendererText()
            columns[n] = gtk.TreeViewColumn(column_names[n], cell)
            columns[n].set_cell_data_func(cell, cell_data_funcs[n])
            self.table_list.append_column(columns[n])

        self.table_list.set_model(tables)

    def __cell_table_id(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 0))

    def __cell_table(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 1))

    def __cell_limit(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 2))

    def __cell_players(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 3))

    def set_status(self, message):
        """ Display a message in the main window's status bar. """
        self.statusbar.push(self.statusbar.get_context_id("Rounder"), message)
        self.statusbar.show()



class ConnectDialog:
    """ Dialog for connecting to a server. """

    def __init__(self, app):

        logger.debug("Opening connect dialog.")

        self.app = app

        glade_file = 'rounder/ui/gtk/data/connect.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        self.connect_dialog = self.glade_xml.get_widget('connect-dialog')

        signals = {
            'on_connect_button_clicked': self.connect,
        }
        self.glade_xml.signal_autoconnect(signals)

        self.connect_dialog.show_all()

    def connect(self, widget):
        """ Attempt to open a connection to the host and port specified. """
        host_entry = self.glade_xml.get_widget('host-entry')
        host = host_entry.get_text()
        port_spinbutton = self.glade_xml.get_widget('port-spinbutton')
        port = port_spinbutton.get_value_as_int()
        username_entry = self.glade_xml.get_widget('username-entry')
        username = username_entry.get_text()
        password_entry = self.glade_xml.get_widget('password-entry')
        password = password_entry.get_text()
        logger.debug("Connecting to %s on port %s" % (host, port))
        logger.debug("   as: %s / %s" % (username, password))

        # Attempt to connect to the specified server by creating a client
        # object. If successful pass the client back to the main application,
        # otherwise display an error status message and let the user try
        # again:
        client = RounderNetworkClient(self.app)
        try:
            client.connect(host, port, username, password)
        except Exception, e:
            logger.error("Unable to login to %s as %s" % (host, username))

    def set_status(self, message):
        """ Display a message in the connect dialog's status bar. """
        statusbar = self.glade_xml.get_widget('statusbar')
        statusbar.push(statusbar.get_context_id("Connect Dialog"), message)
        statusbar.show()

    def destroy(self):
        """
        Called by main Rounder application who receives the success callback
        from the network client.
        """
        self.connect_dialog.destroy()



class TableWindow:
    """ Dialog for a poker table. """

    def __init__(self, app):

        logger.debug("Opening table window.")

        self.app = app

        glade_file = 'rounder/ui/gtk/data/table.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        self.table_window = self.glade_xml.get_widget('table-window')

        #signals = {
        #    'on_connect_button_clicked': self.connect,
        #}
        #self.glade_xml.signal_autoconnect(signals)

        self.table_window.show_all()

