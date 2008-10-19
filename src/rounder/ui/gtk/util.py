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

""" Rounder GTK Utilities """

import os
import sys


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
