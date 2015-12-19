from threading import Thread
from Queue import Queue
from twisted.python import log
import time
import Mailbox, WebSockets
import sys

queue = Queue()
MailboxThread = Thread(target=Mailbox.MailboxHandler, args=(queue,))
WebSocketsThread = Thread(target=WebSockets.WebsocketsHandler, args=(queue,))

MailboxThread.setDaemon(True)
WebSocketsThread.setDaemon(True)

log.startLogging(sys.stdout)

MailboxThread.start()
WebSocketsThread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print "Shutting down..."
        raise
