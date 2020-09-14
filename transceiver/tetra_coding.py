#!/usr/bin/env python3

import ctypes

"""
libcorrect = ctypes.CDLL("../../libcorrect/build/lib/libcorrect.so")

conv = libcorrect.correct_convolutional_create(
    ctypes.c_size_t(4),
    ctypes.c_size_t(5),
    (ctypes.c_uint16 * 4)(0b11001, 0b10111, 0b11101, 0b11011))
"""

# Do the stuff from EN 300 396-2 8.2.5.2
# e is the DM colour code, a byte array or list of length 30
def generate_scrambling_sequence(length, e):
    taps = (1,2,4,5,7,8,10,11,12,16,22,23,26,32)
    # Initialization
    p = [1,1] + list(e) + [0]*length
    if len(p) != 32 + length:
        raise ValueError("e should have a length of 30")
    for k in range(32, 32 + length):
        p[k] = sum(p[k-j] for j in taps) % 2
    return bytes(p[32:])

# Scrambling sequence for synchronization block 1
sb_scrambling = generate_scrambling_sequence(120, [0]*30)

# Convert between type 4 and type 5 bits
def scramble(bits, seq):
    return bytes(((b + seq[i]) % 2) for i, b in enumerate(bits))

descramble = scramble

# Convert type 4 bits to type 3 bits
# according to EN 300 396-2 8.2.4.1
def deinterleave(bits, a = 11):
    K = len(bits)
    return bytes(bits[(a * (i+1)) % K] for i in range(K))

