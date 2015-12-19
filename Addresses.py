import random
from Config import domain

class CustomAddress():
    def get(self):
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
        randEmail = randString + '@' + domain

        return randEmail
