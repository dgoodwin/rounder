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
import gobject

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

        #signals = {
        #    'on_WujaAbout_close': self.__close_about_dialog,
        #}
        #glade_xml.signal_autoconnect(signals)

        main_window.show_all()

    def main(self):
        """ Launches the GTK main loop. """
        gtk.main()
