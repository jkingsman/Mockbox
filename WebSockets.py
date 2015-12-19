from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor, task
from Addresses import CustomAddress
import json

openSockets = []

class WebsocketsHandler():
    def __init__(self, queue):
        factory=WebSocketServerFactory("ws://localhost:9000", debug=False)
        factory.protocol = self.MyServerProtocol

        self.queue = queue

        lc = task.LoopingCall(self.processSockets)
        lc.start(2)

        reactor.listenTCP(9000, factory)
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
            self.sendMessage(self.id.encode("utf8"))

        def onClose(self, wasClean, code, reason):
            print "Client connection closed with " + self.id
            openSockets.remove(self)
