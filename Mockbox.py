from threading import Thread
from Queue import Queue
from twisted.python import log
import time
import Mailbox
import Web
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", "-v", help="output logs to std out, not the file",
                    action="store_true")
args = parser.parse_args()

queue = Queue()
MailboxThread = Thread(target=Mailbox.MailboxHandler, args=(queue,))
WebThread = Thread(target=Web.WebHandler, args=(queue,))

MailboxThread.setDaemon(True)
WebThread.setDaemon(True)

if args.verbose:
    log.startLogging(sys.stdout)
else:
    log.startLogging(open('mockbox.log', 'a'))

MailboxThread.start()
WebThread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print "Shutting down..."
        break
