from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task, ssl
from twisted.web.util import Redirect
from twisted.web.resource import Resource
from Addresses import CustomAddress
import Config
import json

openSockets = []

class WebHandler():
    def __init__(self, queue):
        self.queue = queue

        # set up the handler to drop emails from the message 'queue' into the main processing queue
        lc = task.LoopingCall(self.processSockets)
        lc.start(2)

        # fire up static server while we're here
        staticResource = File('./static/dist')
        staticFactory = Site(staticResource)

        if Config.useSSL:
            contextFactory = ssl.DefaultOpenSSLContextFactory(
                Config.keyFile,
                Config.certFile
            )

            # static HTTPS serving
            reactor.listenSSL(443, staticFactory, contextFactory)

            # WSS
            WSfactory=WebSocketServerFactory(u"wss://localhost:9000", debug=False)
            WSfactory.protocol = self.MyServerProtocol
            listenWS(WSfactory, contextFactory)
        else:
            # static HTTP serving
            reactor.listenTCP(80, staticFactory)

            # WS
            WSfactory.protocol = self.MyServerProtocol
            WSfactory=WebSocketServerFactory(u"ws://localhost:9000", debug=False)
            listenWS(WSfactory)

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
            self.sendMessage(json.dumps([self.id, Config.bindingPort, Config.dropSize]).encode("utf8"))

        def onClose(self, wasClean, code, reason):
            print "Client connection closed with " + self.id
            try:
                # we have some weird issue where this is called twice...
                openSockets.remove(self)
            except ValueError:
                pass
