

from twisted.internet import stdio
from twisted.protocols import basic
from twisted.conch import recvline

class CLIProtocol(recvline.HistoricRecvLine):
    from os import linesep as delimiter

    input_labels = {}
    output_labels = {}

    def __init__(self, service):
        self.service = service
        stdio.StandardIO(self)
        try:
            f = open("crosspoints.dat", "r")
            self.readLabels(f)
        except IOError:
            print "crosspoints.dat not found, no labels loaded"
            pass
        self.commands = {"getxps":self.printCrosspoints,
                "help":self.printHelp,
                "setxp":self.cmdSetCrosspoint}

    def readLabels(self, f):
        for line in f:
            tokens=line.split(':')
            if tokens[0] == '#':
                continue
            if tokens[0] == 'I':
                self.input_labels[int(tokens[1])] = tokens[2].strip()
            if tokens[0] == 'O':
                self.output_labels[int(tokens[1])] = tokens[2].strip()

    def printCrosspoints(self):
        print " {:^28} | {:^28} ".format('INPUT', 'OUTPUT')
        print '-' * 30 + '+' + '-' * 30
        for k, v in self.service.crosspoints.iteritems():
            print "    %02d (%-020s) | %02d (%-020s)" % (
                    k, self.output_labels.get(k, "unlabeled"), 
                    v, self.input_labels.get(v, "unlabeled"))

    def setCrosspoint(self, output, input):
        print "[CLI] Received notification of patch change."

    def cmdSetCrosspoint(self):
        output = int(self.tokens[1])
        input = int(self.tokens[2])
        print "[CLI] Setting output %02d to input %02d." % (output, input)
        self.service.notifyPatch(self, output, input)

    def connectionMade(self):
        print "Router controller ready."
        self.terminal.write('>>> ')

    def invalidCommand(self):
        self.terminal.write("Huh?\n")

    def printHelp(self):
        self.terminal.write("Haha, nope, none of that yet.\n")

    def dataReceived(self, line):
        # this sounds almost dirty...
        self.tokens = line.strip().split()
        if self.tokens:
            self.commands.get(self.tokens[0], self.invalidCommand)()
        self.terminal.write(">>> ")
