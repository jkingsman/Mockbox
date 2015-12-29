import smtpd
import random
import pprint
import asyncore
from email.parser import Parser
from twisted.internet import task
from Config import bindingPort, bindingIP, dropSize

staged = []


class MailboxHandler():
    def __init__(self, queue):
        self.binding = (bindingIP, bindingPort)

        def stagedToQueue():
            while len(staged) > 0:
                queue.put(staged.pop())

        lc = task.LoopingCall(stagedToQueue)
        lc.start(2)

        server = CustomSMTPServer(self.binding, None)
        print 'SMTP starting on', self.binding[1]
        asyncore.loop(timeout=1)


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailFrom, mailTo, data):
        # handle drop conditions
        if len(data) > dropSize:
            # too big; drop
            print 'Dropping message to', mailTo, ': too big'
            return

        # begin assembling email object
        parser = Parser()
        print 'Receiving message from:', mailFrom, peer, 'to', mailTo
        email = parser.parsestr(data)

        emailObj = {}
        emailObj['raw'] = data
        emailObj['from'] = email.get('From')
        emailObj['fromIP'] = peer
        emailObj['to'] = email.get('To')
        emailObj['subject'] = email.get('Subject')
        emailObj['transferEncoding'] = email.get('Content-Transfer-Encoding')
        emailObj['attachments'] = []

        if email.is_multipart():
            # loop through each chunk of the body
            for index, part in enumerate(email.get_payload()):
                if index == 0:
                    # first object of multipart is probably body
                    emailObj['body'] = part.get_payload()
                else:
                    attachment = {}
                    attachment['name'] = part.get_filename()
                    attachment['type'] = part.get_content_type()
                    attachment['data'] = part.get_payload()
                    attachment['transferEncoding'] = part.get('Content-Transfer-Encoding')
                    emailObj['attachments'].append(attachment)
        else:
            # not multipart; grab the body and run
            emailObj['body'] = email.get_payload(decode=True)

        staged.append(emailObj)
        return
