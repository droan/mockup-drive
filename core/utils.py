import binascii
import math
import os


def generate_random_hex(length=10):
    half_length = math.ceil(length / 2)
    return binascii.hexlify(os.urandom(half_length)).decode()[:length]
