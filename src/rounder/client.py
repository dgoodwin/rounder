#!/usr/bin/env python

from twisted.internet import reactor, protocol

class RounderClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write("hello, world!")

    def dataReceived(self, data):
        print "Server said:", data
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "connection lost"

class RounderClientFactory(protocol.ClientFactory):
    protocol = RounderClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed, goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection failed, goodbye!"
        reactor.stop()

def main():
    f = RounderClientFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
