from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task
from Addresses import CustomAddress
from Config import bindingPort, httpPort, dropSize
import json

openSockets = []

class WebHandler():
    def __init__(self, queue):
        factory=WebSocketServerFactory("ws://localhost:9000", debug=False)
        factory.protocol = self.MyServerProtocol

        self.queue = queue

        # set up the handler to drop emails from the message 'queue' into the main processing queue
        lc = task.LoopingCall(self.processSockets)
        lc.start(2)

        reactor.listenTCP(9000, factory)

        # fire up static server while we're here
        resource = File('./static/dist')
        factory = Site(resource)
        reactor.listenTCP(httpPort, factory)

        reactor.run(installSignalHandlers=0) # no handlers because threads

    def processSockets(self):
        while self.queue.qsize() > 0:
            emailEntry = self.queue.get()

            if emailEntry['to'] not in [socket.id for socket in openSockets]:
                print 'Dropping message to', emailEntry['to'] + ': no such box'
            else:
                for openSocket in openSockets:
                    if emailEntry['to'] == openSocket.id:
                        openSocket.sendMessage(json.dumps(emailEntry).encode("utf8"))

    class MyServerProtocol(WebSocketServerProtocol):
        def __init__(self, *args, **kwargs):
            super(WebSocketServerProtocol, self).__init__(*args, **kwargs)
            self.id = CustomAddress().get()

        def onConnect(self, request):
            print "Client connection from " + self.id + " at: {0}".format(request.peer)

        def onOpen(self):
            print "Sent identification to " + self.id
            openSockets.append(self)
            self.sendMessage(json.dumps([self.id, bindingPort, dropSize]).encode("utf8"))

        def onClose(self, wasClean, code, reason):
            print "Client connection closed with " + self.id
            openSockets.remove(self)
