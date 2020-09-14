#!/usr/bin/env python3

import tetra_coding

def print_bits(text, bits):
    print(text, "".join("\033[3%dm%d" % (2+b, b) for b in bits), "\033[0m")

# Bits demodulated from a DMO synchronization burst
burst_str = "00 01 01 00 01 11 10 11 11 11 11 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 11 11 11 00 11 11 11 11 00 01 10 11 11 10 11 01 01 10 10 01 01 00 00 00 01 11 11 10 10 11 11 10 10 11 11 11 10 10 11 10 11 11 10 11 11 01 10 00 10 11 11 00 00 11 11 01 00 10 10 00 11 10 10 11 00 00 01 10 01 11 00 11 10 10 01 11 00 00 01 10 01 11 10 01 11 11 01 11 00 00 11 11 01 10 11 10 00 00 11 11 01 01 10 10 01 01 11 00 10 10 00 10 11 11 10 01 10 01 00 10 11 10 10 01 01 00 00 00 11 01 10 00 01 10 11 00 10 00 10 01 11 00 00 00 01 11 10 01 01 00 10 01 10 10 00 10 01 01 11 11 11 00 01 11 11 01 00 10 00 10 00 01 01 00 11 10 01 00 10 10 01 10 10 10 00 10 11 01 11 10 00"

# Handle the burst as a byte array, each byte representing one bit
burst = bytes(1 if c=="1" else 0 for c in burst_str.replace(" ", ""))

# Split into fields
sb_bits5 = burst[94:214]  # Scrambled synchronization block 1 type 5 bits
bkn2_bits5 = burst[252:468]  # Scrambled block 2 bits

print_bits("Type 5:", sb_bits5)

# Convert to type 4 bits
sb_bits4 = tetra_coding.descramble(sb_bits5, tetra_coding.sb_scrambling)

print_bits("Type 4:", sb_bits4)

# Convert to type 3 bits
sb_bits3 = tetra_coding.deinterleave(sb_bits4, 11)

print_bits("Type 3:", sb_bits3)


# Speedtest
N = 100000

import time
t1 = time.time()

for i in range(N):
    sb_bits5 = burst[94:214]
    sb_bits4 = tetra_coding.descramble(sb_bits5, tetra_coding.sb_scrambling)
    sb_bits3 = tetra_coding.deinterleave(sb_bits4, 11)

t2 = time.time()
print("Descrambled and deinterleaved %f blocks per second" % (N / (t2-t1)))
