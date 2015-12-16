import smtpd
import asyncore
import random
import pprint
from email.parser import Parser
parser = Parser()

binding = ('0.0.0.0', 25)
dropSize = 1000000 # in bytes
domainName = 'mockbox.io'

validAddresses = []

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailFrom, mailTo, data):
        # handle drop conditions
        if len(data) > dropSize:
            # too big; drop
            print 'Dropping message to', mailTo, ': too big'
            return

        if len([x for x in mailTo if x in validAddresses]) == 0:
            # not a valid address
            print 'Dropping message to', mailTo, ': no such address'
            return

        # begin assembling email object
        print 'Receiving message from:', mailFrom, '(', peer, ') to', mailTo
        email = parser.parsestr(data)

        emailObj = {}
        emailObj['raw'] = data
        emailObj['from'] = email.get('From')
        emailObj['fromIP'] = peer
        emailObj['to'] = email.get('To')
        emailObj['subject'] = email.get('Subject')
        emailObj['attachments'] = []

        if email.is_multipart():
            # loop through each chunk of the body
            for index, part in enumerate(email.get_payload()):
                if index == 0:
                    # first object of multipart is probably body
                    emailObj['body'] = email.get_payload(decode=True)
                else:
                    attachment = {}
                    attachment['name'] = part.get_filename()
                    attachment['type'] = part.get_content_type()
                    attachment['data'] = part.get_payload()
                    emailObj['attachments'].append(attachment)

        else:
            # not multipart; grab the body and run
            emailObj['body'] = email.get_payload(decode=True)

        pprint.pprint(emailObj)
        return

def newAddress():
    global validAddresses
    letterCount = 8
    numberCount = 2
    vowels = 'aeiou'
    consonants = 'bcdfgjklmnprstvz' # no hqx for pronouncability
    randString = ''

    for i in range(letterCount):
        if len(randString) == 0:
            randString += random.choice(consonants)
        else:
            if randString[-1:] in consonants:
                randString += random.choice(vowels)
            else:
                randString += random.choice(consonants)

    randString += str(random.randint(10**(numberCount-1), (10**numberCount)-1))
    randEmail = randString + '@' + domainName

    validAddresses.append(randEmail)
    print 'Permitting email ' + randEmail

server = CustomSMTPServer(binding, None)
print 'Mockbox listening on', binding[0], 'on port', binding[1], '(no username or password necessary)'
print 'Messages over', dropSize, 'bytes will be dropped'
print '------------------------------------------------'
newAddress()

asyncore.loop(timeout=1)
