from random import choice, randint
from itertools import product
from Config import domain


class CustomAddress():
    def __init__(self):
        self.vowels = 'aeiou'
        self.consonants = 'bcdfgjklmnprstvz'
        self.choices = map(lambda x: "".join(x), product(self.consonants, self.vowels))
        self.letterCount = 8
        self.numberCount = 2

    def get(self):
        randString = "".join(choice(self.choices) for _ in xrange(self.letterCount / 2))[:self.letterCount] + \
            str(randint(10 ** (self.numberCount - 1), (10 ** self.numberCount) - 1))

        randEmail = randString + '@' + domain
        return randEmail
