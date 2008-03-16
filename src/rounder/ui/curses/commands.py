#!/usr/bin/python

from rounder.ui.curses.main import RounderNetworkClient


class HelpCommand(object):

    name = "help"
    args = None
    summary = "display help messages"

    @staticmethod
    def do(state, args):
        for command in state.commands:
            helpmsg = command.name
            if command.args:
                helpmsg += " " + command.args
            helpmsg += " - %s" % command.summary
            state.screen.write(helpmsg)


class ConnectCommand(object):

    name = "connect"
    args = "server port username password"
    summary = "connect to a server"

    @staticmethod
    def do(state, args):
        host = args[0]
        port = int(args[1])
        username = args[2]
        password = args[3]

        if state.is_connected():
            state.log("Error - Already connected")
            return
        client = RounderNetworkClient(state.servercb)
        client.connect(host, port, username, password)


class ListCommand(object):

    name = "list"
    args = None
    summary = "list tables"

    @staticmethod
    def do(state, args):
        if not state.is_connected():
            state.log("Error - Not connected")
        state.client.get_table_list()


class JoinCommand(object):

    name = "join"
    args = "table_num"
    summary = "join a table"

    @staticmethod
    def do(state, args):
        tableid = int(args[0])

        if not state.is_connected():
            state.log("Error - Not connected")
        state.client.open_table(tableid)


class SitCommand(object):

    name = "sit"
    args = "seat_num"
    summary = "sit in a seat"

    @staticmethod
    def do (state, args):
        seatid = int(args[0])

        if not state.is_connected():
            state.log("Error - Not connected")
        if not state.is_ontable():
            state.log("Error - Not at a table")
        state.table.sit(seatid)


commands = (HelpCommand, ConnectCommand, ListCommand, JoinCommand, SitCommand)
