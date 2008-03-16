#!/usr/bin/env python

import string
import StringIO
import traceback
import sys
import csv

from curses.wrapper import wrapper
import curses

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.python import log

from rounder.network.serialize import register_message_classes
from rounder.network.client import RounderNetworkClient
from rounder.ui.client import Client

class TxtRounderState:

    def __init__(self, screen):
        self.client = None
        self.table = None
        self.commands = TxtRounderCommands(self)
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

class TxtRounderCommands:
    """ Client calls to the server. """

    def __init__(self, state):
        self.state = state

    def help(self):
        self.state.screen.write("help - Supported Commands:")
        self.state.screen.write("connect server port user pass - connect to a server")
        self.state.screen.write("list - list tables")
        self.state.screen.write("join table_num - join a table")
        self.state.screen.write("sit seat_num - sit in a seat")

    def connect(self, host, port, username, password):
        """ Connect to server. """
        if self.state.is_connected():
            self.state.log("Error - Already connected")
            return
        client = RounderNetworkClient(self.state.servercb)
        client.connect(host, port, username, password)

    def list(self):
        """ List tables. """
        if not self.state.is_connected():
            self.state.log("Error - Not connected")
        self.state.client.get_table_list()

    def join(self, tableid):
        if not self.state.is_connected():
            self.state.log("Error - Not connected")
        self.state.client.open_table(tableid)

    def sit(self, seatid):
        if not self.state.is_connected():
            self.state.log("Error - Not connected")
        if not self.state.is_ontable():
            self.state.log("Error - Not at a table")
        self.state.table.sit(seatid)

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

    def got_table_list(self, tables):
        self.screen.write("Table List:")
        for table in tables:
            self.screen.write(str(table))

    def open_table_success_cb(self, table):
        self.screen.write("Joined Table")
        self.state.table = table

class CursesStdIO:
    """fake fd to be registered as a reader with the twisted reactor. """

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def doRead(self):
        """called when input is ready"""

    def logPrefix(self): return 'CursesClient'

class RounderScreen(CursesStdIO):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.idlok(1)
        self.stdscr.scrollok(True)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

        self.input = ""
        self.status = "Disconnected"
        self.rows, self.cols = self.stdscr.getmaxyx()
        # TODO: add check that window is big enough

        self.stdscr.clear()
        self.stdscr.setscrreg(0, self.rows - 3)
        self.display_status()
        self.position_cursor()
        self.stdscr.refresh()

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
        self.input = ""
        self.write(input)
        if not len(input):
            return
        try:
            command = self.create_command(input)
            eval(command, {}, {"x":self.commands})
        except SyntaxError:
            self.write("Invalid Command - Syntax Error")
            self.write(traceback.format_exc())
        except AttributeError:
            self.write("Invalid Command - Attribute Error")
            self.write(traceback.format_exc())
        except Exception:
            self.write(traceback.format_exc())

    def display_status(self):
        status = self.status + ' ' * (self.cols - len(self.status))
        self.stdscr.addnstr(self.rows - 2, 0, status, self.cols,
                curses.color_pair(2))
        self.stdscr.refresh()

    def create_command(self, input):
        s = StringIO.StringIO(input)
        values = csv.reader(s, delimiter=' ').next()
        if not len(values):
            self.write("Invalid Command - None")

        command = "x." + values[0] + "("

        for value in values[1:]:
            if value.isdigit():
                command = command + value + ", "
            elif value.isalnum():
                command = command + "\"" + value + "\", "

        if len(values) > 1:
            command = command[:-2] # remove last ', '

        command = command + ")"
        return command

    def doRead(self):
        c = self.stdscr.getch()

        if (c > 256):
            return

        if c == 8 or c == 127: # Backspace
            if len(self.input):
                self.input = self.input[:-1]
                self.stdscr.delch(self.rows - 1, len(self.input))
        elif c == 10: # Enter
            self.stdscr.deleteln()
            self.handle_input()
        elif chr(c) in string.printable:
            if len(self.input) == self.cols - 2: return
            self.input = self.input + chr(c)
            self.stdscr.insch(self.rows - 1, len(self.input) - 1, chr(c))

        self.position_cursor()
        self.stdscr.refresh()

    def write(self, line, colour = 1):
        self.stdscr.scroll()
        self.stdscr.addstr(self.rows - 3, 0, line, curses.color_pair(colour))
        self.position_cursor()
        self.stdscr.refresh()

class RounderCurses:
    def main(self):
        # TODO: why do I have to do this?
        register_message_classes()
        wrapper(self.startClient)

    def startClient(self, stdscr):
        screen = RounderScreen(stdscr)
        state = TxtRounderState(screen)
        screen.set_command(state.commands)

        reactor.addReader(screen)
        reactor.run()