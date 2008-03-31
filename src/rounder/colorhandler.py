#   Rounder - Poker for the GNOME Desktop
#
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


"""
Colorized multiline logging output.

The format was shamelessly stolen from PackageKit's logger
(http://www.packagekit.org).
"""


import time
from logging import StreamHandler

import curses


curses.setupterm()

color_normal = curses.tigetstr('sgr0')
color_green = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_GREEN)
color_blue = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_BLUE)
color_magenta = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_MAGENTA)
color_red = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_RED)


class ColorStreamHandler(StreamHandler):

    def _select_color(self, level):
        if level < 20:
            return color_magenta
        if level < 30:
            return color_blue
        else:
            return color_red

    def _colorize(self, color, text):
        if not self.stream.isatty():
            return text
        return '%s%s%s' % (color, text, color_normal)

    def format(self, record):
        logtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        # Add on the milliseconds
        logtime += ",%.0f" % ((record.created % 1) * 1000)
        header = "%-23.23s  %-8.8s  %s" % (logtime, record.levelname,
                record.name)
        header = self._colorize(color_green, header)

        color = self._select_color(record.levelno)

        msg = ' - ' + '\n   '.join(record.msg.split('\n'))
        msg = msg % record.args
        msg = self._colorize(color, msg)

        return "%s\n%s" % (header, msg)
