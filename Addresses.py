import random
from numpy import product
from Config import domain

class CustomAddress():
    def __init__(self):
        self.vowels = 'aeiou'
        self.consonants = 'bcdfgjklmnprstvz' # no hqx for pronouncability
        self.choices = map(lambda x: "".join(x), product(self.consonants, self.vowels))
        self.letterCount = 8
        self.numberCount = 2

    def get(self):
        return "".join(choice(self.choices) for _ in xrange(self.letterCount / 2))[:self.letterCount] + \
                       str(randint(10**(self.numberCount-1), (10**self.numberCount)-1))
