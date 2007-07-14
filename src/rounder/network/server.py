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

""" The Rounder Server Module """

from zope.interface import implements
from twisted.spread import pb
from twisted.cred import checkers, portal
from twisted.internet import reactor

from logging import getLogger
logger = getLogger("rounder.network.server")

#from rounder.network.protocol import register_message_classes
from rounder.limit import FixedLimit
from rounder.table import Table
from rounder.currency import Currency

SERVER_PORT = 35100

class RounderNetworkServer:

    """ 
    Core Rounder Server 
    
    Maintains the internal engine objects, as well as the lists of connected
    clients etc.
    """

    def __init__(self):
        self.users = {} # hash of usernames to their perspectives
        self.tables = {}
        self.table_counter = 0 # used to name the tables for now

    def create_table(self):
        
        limit = FixedLimit(small_bet=Currency(1), big_bet=Currency(2))
        self.table_counter += 1
        table_name = "Table %s" % self.table_counter
        table = Table(name=table_name, limit=limit, seats=10)
        self.tables[table_name] = table



class RounderRealm:

    """ Creates perspectives/avatars. """

    implements(portal.IRealm) 
    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User(avatarId, self.server)
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a=avatar:a.detached(mind)



class User(pb.Avatar):

    def __init__(self, name, server):
        logger.info("User authenticated: %s" % name)
        self.name = name
        self.server = server
        self.server.users[self.name] = self

    def attached(self, mind):
        self.remote = mind

    def detached(self, mind):
        self.remote = None

#def perspective_joinGroup(self, groupname, allowMattress=True):
#    return self.server.joinGroup(groupname, self, allowMattress)

    def send(self, message):
        self.remote.callRemote("print", message)

    def perspective_list_tables(self):

        """ Lists available tables. """
        
        tables = []
        for t in self.server.tables.values():
            tables.append(t.name)

        return tables



def run_server():
    logger.info("Starting Rounder server on port %s" % (SERVER_PORT))
    
    realm = RounderRealm()
    realm.server = RounderNetworkServer()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser("joe", "password")
    p = portal.Portal(realm, [checker])

    realm.server.create_table()

    reactor.listenTCP(SERVER_PORT, pb.PBServerFactory(p))
    reactor.run()

