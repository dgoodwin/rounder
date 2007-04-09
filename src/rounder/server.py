#!/usr/bin/env python

from twisted.internet import reactor, protocol

class RounderProtocol(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

def main():
    factory = protocol.ServerFactory()
    factory.protocol = RounderProtocol
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
