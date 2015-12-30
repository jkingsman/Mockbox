from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task, ssl
from twisted.web.util import Redirect
from twisted.web.resource import Resource
from Addresses import CustomAddress
import Config
import json
import os

openSockets = {}


class WebHandler():
    def __init__(self, queue):
        self.queue = queue

        # set up handler to drop emails from the 'queue' into the main queue
        lc = task.LoopingCall(self.processSockets)
        lc.start(2)

        # fire up static server while we're here
        staticResource = File('./static/dist')
        staticFactory = Site(staticResource, logPath=os.devnull)
        staticFactory.noisy = False

        if Config.useSSL:
            contextFactory = ssl.DefaultOpenSSLContextFactory(
                Config.keyFile,
                Config.certFile
            )

            # static HTTPS serving
            reactor.listenSSL(Config.httpsPort, staticFactory, contextFactory)

            # WSS
            WSfactory = WebSocketServerFactory(u"wss://localhost:9000", debug=False)
            WSfactory.protocol = self.MyServerProtocol
            WSfactory.noisy = False
            listenWS(WSfactory, contextFactory)
        else:
            # static HTTP serving
            reactor.listenTCP(Config.httpPort, staticFactory)


            # WS
            WSfactory = WebSocketServerFactory(u"ws://localhost:9000", debug=False)
            WSfactory.protocol = self.MyServerProtocol
            WSfactory.noisy = False
            listenWS(WSfactory)

        # no handlers because threads
        reactor.run(installSignalHandlers=0)

    def processSockets(self):
        while self.queue.qsize() > 0:
            emailEntry = self.queue.get()

            try:
                openSockets[emailEntry['to']].sendMessage(json.dumps(emailEntry).encode("utf8"))
                print 'Dispatching email to', emailEntry['to']
                if Config.logEmail:
                    print "------------------BEGIN MESSAGE DUMP------------------"
                    print json.dumps(emailEntry)
                    print "-------------------END MESSAGE DUMP-------------------"
            except KeyError:
                print 'Dropping message to', emailEntry['to'] + ': no such box'
                pass

    class MyServerProtocol(WebSocketServerProtocol):
        def __init__(self, *args, **kwargs):
            super(WebSocketServerProtocol, self).__init__(*args, **kwargs)
            self.id = CustomAddress().get()

        def onConnect(self, request):
            print "Client connection from " + self.id + " at {0}".format(request.peer)

        def onOpen(self):
            openSockets[self.id] = self
            self.sendMessage(json.dumps([self.id, Config.bindingPort, Config.dropSize]).encode("utf8"))

        def onClose(self, wasClean, code, reason):
            print "Client connection closed with " + self.id
            try:
                del openSockets[self.id]
            except KeyError:
                pass
