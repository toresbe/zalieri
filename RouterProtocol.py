# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 formatoptions+=or autoindent textwidth=132
# 
# This is a twisted Protocol module implementing a small subset of the very small 
# VikinX NCP router control protocol.
#
# 
#
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol
import struct

SERIAL_DEVICE = '/dev/ttyS0'

class RouterProtocol (Protocol):
    # Since Twisted dataReceived events are sent subject to the serialport 
    # library's own buffering, one cannot read bytes from the stream as the 
    # program state requires it; one simply gets n bytes of data and is left
    # to figure out the rest.
    # 
    # Since the program flow therefore becomes disconnected from the state
    # of the data buffer, I have thought it necessary to implement this module
    # as a state engine.
    #
    # The state engine is implemented by a function pointer "nextFunction", which 
    # is set to an appropriate value as the code state progresses. There should be 
    # a timeout of about ten seconds or so which will reset the nextFunction to 
    # a default state in order to ameliorate the concequences of random interestingness.
    
    # Some constants used for forming the commands.
    NCP_GET_XPS = 0xC0
    # FIXME: As you can see, the router is statically addressed in the code as address
    # zero. Until such time that Frikanalen can afford more than the one I found in a dumpster,
    # that's all I'll implement.
    ROUTER_ADDR = 0x00
    
    # Contains the temporary state of the crosspoint set command in between the
    # receipt of the output byte and the input byte.
    crosspointOutput=0
    
    def invalidData(self, byte):
        # Ruh roh.
        print "Received invalid data from the serial port interface."
    
    def parseByte(self, byte):
        # This function is the default function called whenever 
        # a byte arrives from the router and we are not expecting
        # any other data.
        #
        # The least significant nybble of an incoming command will 
        # be the address of the router. Since we only have one router
        # so far, I'm not going to bother coding in multi-router
        # support at first.
        command = byte & 0xF0
        #print "[RTR] Byte is command %02X" % command
        self.setNextFunction(self.command_dictionary.get(command, self.invalidData))
    
    def __init__(self, service):
        # This defines the function to be called upon next byte
        self.service = service
        SerialPort(self, SERIAL_DEVICE, service.reactor, timeout=5)
        self.nextFunction=self.parseByte
    
        # This is the matrix defining the relationship between incoming command
        # nybbles and the function which handles them.
        self.command_dictionary = {
            0xA0 : self.getCrosspointOutput,
            0xC0 : self.getCrosspointMessage}
    
    def getCrosspointMessage(self, byte):
        # The router will simply echo the command back to us afterwards. We
        # don't care, but there might be some logging to do at some point or
        # something. ...I dunno. But with this verbose comment, I've added
        # several lines of data to this file, which makes it look more impressive.
        pass
    
    def setCrosspoint(self, output, input):
        # The "Set crosspoint" command is a three-byte command.
        # The first byte has the command in the most significant nybble
        # and the router address in the least significant nybble.
        # The subsequent two bytes are the output and input, respectively.
        print "[RTR] Received notification of patch change."
        self.transport.write(struct.pack("BBB", (0xA0 | self.ROUTER_ADDR), output-1, input-1));
    
    def setNextFunction(self, function):
        # This sets the next function to be used, and also sets a timeout
        # variable, so that if no data has arrived, the module resets to the
        # default state.
        # 
        # TODO: implement the timeout
        #
        self.nextFunction=function
    
    def getCrosspointOutput(self, byte):
        # This function stores the crosspoint output byte and prepares to
        # accept the input crosspoint associated with that output.
        self.crosspointOutput=byte+1
        #print "[RTR] - Setting crosspoint output to %02d" % byte
        self.setNextFunction(self.getCrosspointInput)
    
    def getCrosspointInput(self, input):
        #print "[RTR] - Setting crosspoint input to %02d" % byte
        self.service.notifyPatch(self, self.crosspointOutput, input+1)
        self.setNextFunction(self.parseByte)
    
    def connectionMade(self):
        # We've gotten a connection. Time to send out a command that will get
        # us a list of crosspoints to populate the class instance state.
        #print "[RTR] Connection made! Asking for crosspoint dump..."
        self.transport.write(struct.pack("BB", (self.NCP_GET_XPS | self.ROUTER_ADDR), 0));
    
    def dataReceived(self, data):
        #print "[RTR] Received %d bytes." % len(data)
        for c in data:
            self.nextFunction(struct.unpack("B",c)[0])
