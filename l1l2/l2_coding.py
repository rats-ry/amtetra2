#!/usr/bin/env python3

# This file contains functions used for conversion between type-1 and type-5
# bits in lower MAC. These process individual bursts or blocks, and don't
# store state in between calls.

import ctypes
import numpy as np

libcorrect = ctypes.CDLL("../../libcorrect/build/lib/libcorrect.so")
libcorrect.correct_convolutional_create.restype = ctypes.c_void_p
libcorrect.correct_convolutional_create.argtypes = (ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint16))
libcorrect.correct_convolutional_decode_soft.restype = ctypes.c_ssize_t
libcorrect.correct_convolutional_decode_soft.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p)

# Create a codec for the rate 1/4 mother code
conv_1_4 = libcorrect.correct_convolutional_create(
    4, # Inverse rate
    5, # Order
    (ctypes.c_uint16 * 4)(0b10011, 0b11101, 0b10111, 0b11011)  # Polynomials
    )

def generate_scrambling_sequence(length, e):
    """Do the stuff from EN 300 396-2 8.2.5.2.
    e is the DM colour code, an array or list of length 30."""

    taps = (1,2,4,5,7,8,10,11,12,16,22,23,26,32)
    # Initialization
    p = [1,1] + list(e) + [0]*length
    if len(p) != 32 + length:
        raise ValueError("e should have a length of 30")
    for k in range(32, 32 + length):
        p[k] = sum(p[k-j] for j in taps) % 2
    # TODO: Maybe the whole calculation above could be done with numpy arrays
    return np.array(p[32:], dtype=np.uint8)

# Scrambling sequence for synchronization block 1
sb_scrambling = generate_scrambling_sequence(120, [0]*30)

def scramble(bits, seq):
    """Convert between type 4 and type 5 bits"""
    return bits ^ seq

def scramble_soft(bits, seq):
    """Convert between type 4 and type 5 soft bits"""
    return bits ^ (seq * 0xFF)

# Descrambling and scrambling are actually the same operations,
# so just use the same functions and give them another name.
descramble = scramble
descramble_soft = scramble_soft

def deinterleave(bits, a = 11):
    """Convert type 4 bits to type 3 bits
    according to EN 300 396-2 8.2.4.1"""
    # TODO: write this as a vector operation too, taking an interleaving pattern
    K = len(bits)
    return np.fromiter((bits[(a * (i+1)) % K] for i in range(K)), dtype=np.uint8)


def hard_to_soft(bits):
    """Convert hard bits (0 or 1) to soft bits (0-0xFF).
    Both are numpy arrays with dtype=np.uint8."""
    return np.array((0, 0xFF), dtype=np.uint8)[bits]

def soft_to_hard(softbits):
    """Convert soft bits (0-0xFF) to hard bits (0 or 1).
    Both are numpy arrays with dtype=np.uint8."""
    return (softbits >= 0x80).astype(np.uint8)


def generate_puncturing_pattern(K3, rate = (2,3)):
    """Generate a puncturing pattern for rate 2/3.
    Parameter K3 is the length of a punctured codeword.
    Return a tuple, where first item is the number of bits in an unpunctured
    codeword, and second item is a numpy array that maps bit positions
    in a punctured codeword into bit positions in an unpunctured codeword."""

    # TODO: Other rates
    if rate != (2,3):
        raise ValueError("Only rate 2/3 is implemented for now")

    # Parameters
    K2 = int(K3 * 2 / 3)
    t = 3
    P = (None, 1, 2, 5)

    pattern = np.zeros(K3, dtype=np.int)
    for j in range(1, 1+K3):
        i = j
        k = 8 * ((i - 1) // t) + P[i - t * ((i - 1) // t)]
        pattern[j-1] = k-1

    return (4 * K2, pattern)

def depuncture(b3, pattern):
    """Depuncture type 3 soft bits using a puncturing pattern.
    Soft bits should be a numpy array with dtype=np.uint8."""

    # Mark everything that does not get filled as an erasure (0x80).
    # Add 16 extra erasures in the end, since the libcorrect decoder
    # seems to need them to decode the last bits correctly.
    v = np.full(pattern[0] + 16, 0x80, dtype=np.uint8)
    v[pattern[1]] = b3
    return v


def decode_1_4(softbits):
    """Decode rate 1/4 mother code"""
    if softbits.dtype != np.uint8:
        raise TypeError("dtype should be uint8")
    decoded = np.zeros(len(softbits), dtype=np.uint8) # TODO: proper size
    n_decoded = libcorrect.correct_convolutional_decode_soft(
        conv_1_4, # Codec
        ctypes.c_char_p(softbits.ctypes.data), # Encoded soft bits
        len(softbits), # Number of encoded bits
        ctypes.c_char_p(decoded.ctypes.data), # Buffer for decoded data
    )

    # libcorrect returns 8 bits packed into a byte,
    # but we want just 1 bit per byte, so unpack
    return np.unpackbits(decoded[0:10], bitorder="big")[0:76]


def crc16(bits):
    """(K1+16, K1) block code from EN 300 396-2 8.2.3.2, i.e. CRC"""
    crc = 0xFFFF  # Shift register stored as an integer
    CRCPOLY = 0x8408
    for b in bits:
        crc = (crc >> 1) ^ (CRCPOLY if ((b ^ crc) & 1) else 0)
    crc ^= 0xFFFF
    return np.fromiter((((crc >> i) & 1) for i in range(16)), dtype=np.uint8)
