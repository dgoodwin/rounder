# encoding=utf-8
#
#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2008 James Bowes <jbowes@dangerouslyinc.com>
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

from logging import getLogger
logger = getLogger("rounder.ui.gtk.main")
from twisted.internet import gtk2reactor
gtk2reactor.install()

from rounder.network.client import RounderNetworkClient
from rounder.network.serialize import register_message_classes
from rounder.ui.client import Client
from rounder.ui.gtk.util import find_file_on_path
from rounder.ui.gtk.table import TableWindow

ROUNDER_LOGO_FILE = "rounder/ui/gtk/data/rounder-logo.png"
ROUNDER_ICON_FILE = "rounder/ui/gtk/data/rounder-icon.svg"

def connect(host, port, username, password, app):
        # Attempt to connect to the specified server by creating a client
        # object. If successful pass the client back to the main application,
        # otherwise display an error status message and let the user try
        # again:
        client = RounderNetworkClient(app)
        try:
            client.connect(host, port, username, password)
        except Exception, e:
            logger.error("Unable to login to %s as %s" % (host, username))

class RounderGtk(Client):
    """ 
    The Rounder GTK Client 

    Represents the main Rounder interface to connect to a server, view
    available tables, and join them. (opening a separate window)
    """

    def __init__(self, host=None, port=None, username=None, password=None):

        logger.info("Starting rounder.")
        logger.debug("Initial connection Info:\n"
                     "   host = %s\n"
                     "   port = %s\n"
                     "   username = %s\n"
                     "   password = %s", host, port, username, password)
        register_message_classes()

        glade_file = 'rounder/ui/gtk/data/rounder.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))

        main_window = self.glade_xml.get_widget('main-window')
        main_window.set_icon_from_file(find_file_on_path(ROUNDER_ICON_FILE))
        self.table_list = self.glade_xml.get_widget('table-list')
        self.statusbar = self.glade_xml.get_widget('statusbar')
        self.connect_button = self.glade_xml.get_widget('connect-button')
        logo = self.glade_xml.get_widget("rounder-logo-image")
        logo.set_from_file(find_file_on_path(ROUNDER_LOGO_FILE))

        signals = {
            'on_connect_activate': self.show_connect_dialog,
            'on_close_activate': self.shutdown,
            'on_main_window_destroy' : self.shutdown,
            'on_connect_button_clicked': self.show_connect_dialog,
            'on_quit_button_clicked': self.shutdown,
            'on_table_list_row_activated': self.open_table,
            'on_about1_activate': self.open_about_window,
        }
        self.glade_xml.signal_autoconnect(signals)

        treeselection = self.table_list.get_selection()
        treeselection.set_mode(gtk.SELECTION_SINGLE)

        # Reference to a network client.
        self.client = None

        self.connect_dialog = None # Set once connect dialog is open

        self.set_status("Connect to a server to begin playing.")

        main_window.show_all()

        # Autoconnect if given details, otherwise show connect dialog:
        if host != None and port != None and username != None and \
                password != None:
            connect(host, port, username, password, self)
        else:
            self.show_connect_dialog(None)

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
        logger.debug("row clicked: %s\n"
                     "table id: %s\n"
                     "table name: %s", row[0], model[row][0], model[row][1])
        self.client.open_table(model[row][0])

    def open_table_success(self, client_table):
        table_win = TableWindow(self, client_table)

    def show_connect_dialog(self, widget):
        """ Opens the connect to server dialog. """
        if self.connect_dialog == None:
            self.connect_dialog = ConnectDialog(self)
        else:
            logger.debug("Connect dialog already open.")

    def connect_success(self, client):
        """ 
        Callback used by the connect dialog after a connection to a server
        has been successfully made.
        """
        logger.info("Connected to %s:%s as %s" % (client.host, client.port, 
            client.username))
        self.client = client

        # Call also sets our reference to None:
        if self.connect_dialog != None:
            self.connect_dialog.destroy(None, None, None)
        self.connect_button.set_sensitive(False)

        self.set_status("Connected to server: %s" % client.host)

        server_label = self.glade_xml.get_widget('server-label')
        server_label.set_text(client.host)
        username_label = self.glade_xml.get_widget('username-label')
        username_label.set_text(client.username)

        self.client.get_table_list()

    def connect_failure(self):
        """ Connection failed callback. """
        logger.warn("Connect failed")
        self.connect_dialog.set_status("Login failed.")

    def list_tables_success(self, table_listings):
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

    def open_about_window(self, menuitem):
        # XXX set the url and email dialog hooks
        about = gtk.AboutDialog()

        about.set_name("Rounder")
        about.set_version("0.0.1")
        about.set_copyright("Copyright © 2008 Devan Goodwin & James Bowes")
        about.set_comments("Poker for the GNOME Desktop")
        # XXX Put the full license in here
        about.set_license("GPLv2")
        about.set_website("http://dangerouslyinc.com")
        about.set_website_label("http://dangerouslyinc.com")
        about.set_authors(('Devan Goodwin <dgoodwin@dangerouslyinc.com>',
            'James Bowes <jbowes@dangerouslyinc.com>',
            'Kenny MacDermid <kenny@kmdconsulting.ca>'))
        about.set_artists(('Anette Goodwin <anette.goodwin@gmail.com>',
            'James Bowes <jbowes@dangerouslyinc.com>'))
        about.set_logo(gtk.gdk.pixbuf_new_from_file(
            find_file_on_path(ROUNDER_LOGO_FILE)))

        about.set_icon_from_file(find_file_on_path(ROUNDER_ICON_FILE))

        about.connect('response', lambda x,y: about.destroy())
        about.show_all()

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
        self.connect_dialog.set_icon_from_file(
                find_file_on_path(ROUNDER_ICON_FILE))

        signals = {
            'on_connect_button_clicked': self.connect,
        }
        self.glade_xml.signal_autoconnect(signals)
        self.connect_dialog.connect("delete_event", self.destroy)

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
        logger.debug("Connecting to %s on port %s"
                     "\n   as: %s / %s", host, port, username, password)

        connect(host, port, username, password, self.app)

    def set_status(self, message):
        """ Display a message in the connect dialog's status bar. """
        statusbar = self.glade_xml.get_widget('statusbar')
        statusbar.push(statusbar.get_context_id("Connect Dialog"), message)
        statusbar.show()

    def destroy(self, widget, event, data=None):
        """
        Called by main Rounder application who receives the success callback
        from the network client.
        """
        logger.debug("Closing connect dialog.")
        self.app.connect_dialog = None
        self.connect_dialog.destroy()
