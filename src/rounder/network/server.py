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

SERVER_PORT = 35100

class RounderNetworkServer:

    """ Core Rounder Server """

    def __init__(self):
        pass

    def joinTable(self):
        pass



class RounderRealm:

    """ Creates perspectives/avatars. """

    implements(portal.IRealm) 
    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User(avatarId)
        avatar.server = self.server
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a=avatar:a.detached(mind)



class User(pb.Avatar):
    def __init__(self, name):
        self.name = name
    def attached(self, mind):
        self.remote = mind
    def detached(self, mind):
        self.remote = None
#def perspective_joinGroup(self, groupname, allowMattress=True):
#    return self.server.joinGroup(groupname, self, allowMattress)
    def send(self, message):
        self.remote.callRemote("print", message)



def run_server():
    logger.info("Starting Rounder server on port %s" % (SERVER_PORT))
    
    realm = RounderRealm()
    realm.server = Server()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser("joe", "password")
    p = portal.Portal(realm, [checker])

    reactor.listenTCP(SERVER_PORT, pb.PBServerFactory(p))
    reactor.run()

