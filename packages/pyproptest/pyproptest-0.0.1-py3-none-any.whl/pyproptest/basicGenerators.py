import random
import sys
import string as st

def intArb(minBound = -sys.maxsize, maxBound = sys.maxsize):
    """
    function for creating a random number generator.
    """
    def gen():
        while True:
            yield random.randint(minBound, maxBound)
    return gen

def strArb(maxLength = 100):
    """
    function for creating a random string generator.
    """
    def gen():
        while True:
            yield "".join([random.choice(st.ascii_letters + st.punctuation)\
            for i in range(random.randint(0, maxLength))])
    return gen

def charArb():
    """
    function for creating a random character generator.
    """
    def gen():
        while True:
            yield random.choice(st.ascii_letters + st.punctuation)
    return gen

def floatArb():
    """
    function for creating a random float generator.
    """
    def gen():
        while True:
            return random.random()
    return gen

def intInc(start = 0, increment = 1):
    """
    function for creating an incrementing integer generator.
    """
    def gen():
        i = start
        while True:
            yield i
            i += increment
    return gen

def intListArb(maxlen = 100, minBound = -sys.maxsize, maxBound = sys.maxsize):
    def gen():
        while True:
            l = [random.randint(minBound, maxBound) for i in range(
                random.randint(0, maxlen))]
            yield l
    return gen