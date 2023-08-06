import hashlib
import random

def hash(text):
    text1 = text.encode()
    h = hashlib.sha512(text1)
    return int(h.hexdigest(), base=16)


def authrand():
    return random.randint(1, 10000000000000000000000000000000000000000)


def verify(rand, key, response):
    correct = hash(str(rand*key))
    return response == correct


def authenticte_self(key, rand):
    return hash(str(rand*key))

