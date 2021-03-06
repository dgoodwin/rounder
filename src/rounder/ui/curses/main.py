#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2008 Kenny MacDermid <kenny@kmdconsulting.ca>
#   Copyright (C) 2008 James Bowes <jbowes@dangerouslyinc.com>
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
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

#!/usr/bin/env python

import string
import traceback

from curses.wrapper import wrapper
import curses

from twisted.internet import reactor

from rounder.network.serialize import register_message_classes
from rounder.network.client import RounderNetworkClient
from rounder.ui.client import Client

from rounder.ui.curses import commands


class TxtRounderState(object):

    def __init__(self, screen):
        self.client = None
        self.table = None
        self.commands = commands.commands
        self.servercb = TxtRounderClientServerCallback(self, screen)
        self.screen = screen

    def is_connected(self):
        if self.client is None:
            return False
        return True
        # TODO: other checks

    def is_ontable(self):
        if self.table is None:
            return False
        return True

    def write(self, message):
        self.screen.write(message)

    def log(self, message):
        # TODO: write in different colour
        self.screen.write(message)


class TxtRounderClientServerCallback(Client):

    def __init__(self, state, screen):
        self.screen = screen
        self.state = state

    # Server Callbacks

    def log_error(self, failure):
        self.screen.write("ERROR")
        self.screen.write(str(failure.getTraceback()))

    def connect_success(self, client):
        self.screen.write("Connected")
        self.screen.set_status("Connected")
        self.state.client = client

    def connect_failure(self):
        # TODO: would we have a reason?
        self.screen.write("Login Failed")

    def list_tables_success(self, tables):
        self.screen.write("Table List:")
        for table in tables:
            self.screen.write(str(table))

    def open_table_success(self, table):
        self.screen.write("Joined Table")
        self.state.table = table

    def sit_success(self, seat_number):
        self.screen.write("Took seat %d" % seat_number)

    def process_event(self, event):
        # XXX Do something here
        pass


class CursesStdIO(object):
    """fake fd to be registered as a reader with the twisted reactor. """

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def doRead(self):
        """called when input is ready"""

    def logPrefix(self):
        return 'CursesClient'


class RounderScreen(CursesStdIO):

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.idlok(1)
        self.stdscr.scrollok(True)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

        self.state = None

        self.input = ""
        self.status = "Disconnected"
        self.rows, self.cols = self.stdscr.getmaxyx()
        # TODO: add check that window is big enough

        self.stdscr.clear()
        self.stdscr.setscrreg(0, self.rows - 3)
        self.display_status()
        self.position_cursor()
        self.stdscr.refresh()

        self.history = []
        self.history_pos = 0

    def set_command(self, commands):
        self.commands = commands

    def set_status(self, message):
        self.status = message
        self.display_status()

    def position_cursor(self):
        """ Move to the end of the current input. """
        self.stdscr.move(self.rows - 1, len(self.input))

    def handle_input(self):
        input = self.input
        self.history.append(input)
        self.history_pos = 0
        self.input = ""
        self.write(input)
        if not len(input):
            return
        try:
            command_name, args = self.create_command(input)
            for command in self.commands:
                if command.name == command_name:
                    command.do(self.state, args)
                    break
            else:
                self.write("Invalid Command %s - no such command"
                        % command_name)
        except Exception:
            self.write(traceback.format_exc())

    def display_status(self):
        status = self.status + ' ' * (self.cols - len(self.status))
        self.stdscr.addnstr(self.rows - 2, 0, status, self.cols,
                curses.color_pair(2))
        self.stdscr.refresh()

    def create_command(self, input):
        values = input.split(' ')
        if len(values) == 0:
            self.write("Invalid Command - None")

        return values[0], values[1:] or None

    def doRead(self):
        c = self.stdscr.getch()

        if c in (8, 127, 263): # Backspace
            if len(self.input):
                self.input = self.input[:-1]
                self.stdscr.delch(self.rows - 1, len(self.input))
        elif c == 10: # Enter
            self.stdscr.deleteln()
            self.handle_input()
        elif c == 9: # Tab
            if len(self.input):
                completions = [x.name for x in self.commands \
                        if x.name.startswith(self.input)]
                if len(completions) == 1:
                    self.input = completions[0]
                    self.stdscr.deleteln()
                    self.stdscr.addstr(self.rows - 1, 0, self.input)
        elif c == 259: # Up arrow
            if self.history_pos < len(self.history):
                self.history_pos += 1
                self.stdscr.deleteln()
                self.input = self.history[-self.history_pos]
                self.stdscr.addstr(self.rows - 1, 0, self.input)
        elif c == 258: # Down arrow
            if self.history_pos > 1:
                self.history_pos -= 1
                self.stdscr.deleteln()
                self.input = self.history[-self.history_pos]
                self.stdscr.addstr(self.rows - 1, 0, self.input)
            else:
                self.history_pos = 0
                self.stdscr.deleteln()
                self.input = ""
        elif c < 256 and chr(c) in string.printable:
            if len(self.input) == self.cols - 2:
                return
            self.input = self.input + chr(c)
            self.stdscr.insch(self.rows - 1, len(self.input) - 1, chr(c))
        else:
            return

        self.position_cursor()
        self.stdscr.refresh()

    def write(self, line, colour = 1):
        self.stdscr.scroll()
        self.stdscr.addstr(self.rows - 3, 0, line, curses.color_pair(colour))
        self.position_cursor()
        self.stdscr.refresh()

    def connectionLost(self, why):
        pass


class RounderCurses(object):

    def __init__(self, host=None, port=None, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def main(self):
        # TODO: why do I have to do this?
        register_message_classes()
        wrapper(self.startClient)

    def startClient(self, stdscr):
        screen = RounderScreen(stdscr)
        state = TxtRounderState(screen)
        screen.state = state
        screen.set_command(state.commands)

        reactor.addReader(screen)
        if (self.host and self.port and self.username and self.password):
            client = RounderNetworkClient(state.servercb)
            reactor.callWhenRunning(client.connect, self.host, self.port,
                    self.username, self.password)

        reactor.run()
