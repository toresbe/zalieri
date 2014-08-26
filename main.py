#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 formatoptions+=or autoindent textwidth=132

from RouterAJAX import WebService
from RouterProtocol import RouterProtocol
from RouterCLI import CLIProtocol
from twisted.internet import reactor
from twisted.protocols import basic


class WebInterface():
    def setCrosspoint(output, input):
        pass

class RouterService():
    subscribers = []
    crosspoints = {}

    def addProtocol(self, protocol):
        print "Adding protocol %s" % repr(protocol)
        self.subscribers.append(protocol(self))

    def notifyPatch(self, source, output, input):
        print "[SRV] Received an order to patch output %01d to input %01d." % (output, input)
        self.crosspoints[output]=input
        for subscriber in self.subscribers:
            if subscriber != source:
                subscriber.setCrosspoint(output, input)
        
    def __init__(self):
        self.reactor=reactor

def main():
    print "Running"

    rserv = RouterService()
    rserv.addProtocol(CLIProtocol)
    rserv.addProtocol(RouterProtocol)
    rserv.addProtocol(WebService)
    rserv.reactor.run()

if __name__ == '__main__':
    main()
