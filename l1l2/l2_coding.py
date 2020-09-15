#!/usr/bin/env python3

# This file contains functions used for conversion between type-1 and type-5
# bits in lower MAC. These process individual bursts or blocks, and don't
# store state in between calls.

import ctypes

libcorrect = ctypes.CDLL("../../libcorrect/build/lib/libcorrect.so")

# Create a codec for the rate 1/4 mother code
conv_1_4 = libcorrect.correct_convolutional_create(
    ctypes.c_size_t(4), # Inverse rate
    ctypes.c_size_t(5), # Order
    (ctypes.c_uint16 * 4)(0b10011, 0b11101, 0b10111, 0b11011)  # Polynomials
    )

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



def hard_to_soft_bit(bit):
    return 0xFF if bit else 0x00

def soft_to_hard_bit(softbit):
    return 1 if softbit >= 0x80 else 0

def hard_to_soft(bits):
    return bytes(map(hard_to_soft_bit, bits))

def soft_to_hard(softbits):
    return bytes(map(soft_to_hard_bit, softbits))


# Depuncturing for rate 2/3. Input should be soft bits.
# TODO: other rates
def depuncture_2_3(b3):
    # Parameters
    K3 = len(b3)
    K2 = int(K3 * 2 / 3)
    t = 3
    P = (None, 1, 2, 5)

    # Mark everything that does not get filled as an erasure (0x80).
    # Add 16 extra erasures in the end, since the libcorrect decoder
    # seems to need them to decode the last bits correctly.
    V = [0x80] * (4 * K2 + 16)

    for j in range(1, 1+K3):
        i = j
        k = 8 * ((i - 1) // t) + P[i - t * ((i - 1) // t)]
        V[k-1] = b3[j-1]

    return bytes(V)


# Decode rate 1/4 mother code
def decode_1_4(softbits):
    decoded = ctypes.create_string_buffer(len(softbits)) # TODO: proper size
    n_decoded = libcorrect.correct_convolutional_decode_soft(
        conv_1_4, # Codec
        ctypes.c_char_p(softbits), # Encoded soft bits
        ctypes.c_size_t(len(softbits)), # Number of encoded bits
        decoded, # Buffer for decoded data
    )

    # libcorrect returns 8 bits packed into a byte,
    # but we want just 1 bit per byte, so unpack
    return bytes(((decoded[i // 8][0] >> (7 - (i % 8))) & 1) for i in range(76))


# (K1+16, K1) block code from EN 300 396-2 8.2.3.2, i.e. CRC
def crc16(bits):
    crc = 0xFFFF  # Shift register stored as an integer
    CRCPOLY = 0x8408
    for b in bits:
        crc = (crc >> 1) ^ (CRCPOLY if ((b ^ crc) & 1) else 0)
    crc ^= 0xFFFF
    return bytes(((crc >> i) & 1) for i in range(16))
