import random

from hashlib import sha256

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Generates a string of letters
def generate_string(length):
    out_string = ''
    for i in range(length):
        out_string += random.choice(list(LETTERS))
    return out_string

# Transforms a file into a sha-256 hash
def get_file_hash(file):
    sha256_hash = sha256()

    for chunk in iter(lambda: file.read(4096), b""):
        sha256_hash.update(chunk)

    return sha256_hash.hexdigest()
