# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 formatoptions+=or autoindent textwidth=132
from twisted.web import server, resource, http
from twisted.web.static import File
from twisted.web.resource import Resource

class RouterAJAX():
    def __init__(self, service):
        self.service = service


class WebService(Resource):
    isLeaf = True

    def setCrosspoint(self, output, input):
        pass
    def render_GET(self, request):
        return self.render_POST(request)
    def render_POST(self, request):
        output = int(request.args["output"][0])
        input = int(request.args["input"][0])
        print(repr(input), repr(type(input)))
        # XXX: Returner denne funksjonen success etc?
        # Muligens den burde returne en deferred som sier ifra hvordan det gikk
        self.service.notifyPatch(self, output, input)
        return "Success"
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service
    	resource = File('web')
    	resource.putChild("ajax", self)
    	factory = server.Site(resource)
    	service.reactor.listenTCP(8888, factory)

    
#from twisted.web import server, resource, http
#
#class RootResource(resource.Resource):
#    def __init__(self):
#        resource.Resource.__init__(self)
#        self.putChild('router', RouterHandler())
#
#class TestHandler(resource.Resource):
#    isLeaf = True
#
#    def __init__(self):
#        resource.Resource.__init__(self)
#    def render_GET(self, request):
#        return self.render_POST(request)
#    def render_POST(self, request):
#        return "hello world!"
#        
#
#    from twisted.internet import reactor
#    reactor.listenTCP(8082, server.Site(RootResource()))
#
