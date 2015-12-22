from threading import Thread
from Queue import Queue
from twisted.python import log
import time
import Mailbox, Web
import sys

queue = Queue()
MailboxThread = Thread(target=Mailbox.MailboxHandler, args=(queue,))
WebThread = Thread(target=Web.WebHandler, args=(queue,))

MailboxThread.setDaemon(True)
WebThread.setDaemon(True)

log.startLogging(open('mockbox.log', 'w'))

MailboxThread.start()
WebThread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print "Shutting down..."
        raise
