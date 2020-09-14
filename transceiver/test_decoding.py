#!/usr/bin/env python3

import tetra_coding

def print_bits(text, bits):
    print(text, "".join("\033[3%dm%d" % (2+b, b) for b in bits), "\033[0m")

def softbit_to_text(b):
    if b < 0x40:
        return "\033[1;32m0"
    elif b < 0x60:
        return "\033[0;32m0"
    elif b < 0x80:
        return "\033[0;32m-"
    elif b < 0xA0:
        return "\033[0;33m-"
    elif b < 0xC0:
        return "\033[0;33m1"
    else:
        return "\033[1;33m1"

def print_softbits(text, softbits):
    print(text, "".join(map(softbit_to_text, softbits)), "\033[0m")

# Bits demodulated from DMO synchronization bursts
burst_strs = [
    "00 01 01 00 01 11 10 11 11 11 11 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 11 11 11 00 11 11 11 11 00 01 10 11 11 10 11 01 01 10 10 01 01 00 00 00 01 11 11 10 10 11 11 10 10 11 11 11 10 10 11 10 11 11 10 11 11 01 10 00 10 11 11 00 00 11 11 01 00 10 10 00 11 10 10 11 00 00 01 10 01 11 00 11 10 10 01 11 00 00 01 10 01 11 10 01 11 11 01 11 00 00 11 11 01 10 11 10 00 00 11 11 01 01 10 10 01 01 11 00 10 10 00 10 11 11 10 01 10 01 00 10 11 10 10 01 01 00 00 00 11 01 10 00 01 10 11 00 10 00 10 01 11 00 00 00 01 11 10 01 01 00 10 01 10 10 00 10 01 01 11 11 11 00 01 11 11 01 00 10 00 10 00 01 01 00 11 10 01 00 10 10 01 10 10 10 00 10 11 01 11 10 00",
    "00 01 01 00 01 11 10 11 11 11 11 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 11 11 11 00 01 11 11 11 00 01 10 11 11 10 11 01 01 10 11 01 01 00 00 00 10 11 01 10 10 10 01 11 10 11 10 11 10 10 11 10 11 11 10 11 11 00 00 00 10 11 11 11 00 11 11 01 01 00 11 00 11 10 01 11 00 00 01 10 01 11 00 11 10 10 01 11 00 00 01 10 01 11 10 01 11 11 01 11 00 00 11 11 01 10 11 10 00 00 11 11 01 01 10 10 01 01 11 00 10 10 00 10 11 11 10 01 10 01 00 10 11 10 10 01 01 00 00 00 11 01 10 00 01 10 11 00 10 00 10 01 11 00 00 00 01 11 10 01 01 00 10 01 10 10 00 10 01 01 11 11 11 00 01 11 11 01 00 10 00 10 00 01 01 00 11 10 01 00 10 10 01 10 10 10 00 10 11 01 11 10 00",
    "00 01 01 00 01 11 01 11 11 11 11 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 11 11 11 00 11 11 11 11 10 00 10 11 11 00 11 01 01 10 11 11 00 00 00 01 10 11 01 10 10 01 11 10 10 11 11 01 10 10 11 10 00 11 10 11 11 00 00 01 10 11 11 11 00 01 11 01 00 00 11 00 11 10 10 11 00 00 01 10 01 11 00 11 10 10 01 11 00 00 01 10 01 11 10 01 11 11 01 11 00 00 11 11 01 10 11 10 00 00 11 11 01 01 10 10 01 01 11 00 10 10 00 10 11 11 10 01 10 01 00 10 11 10 10 01 01 00 00 00 11 01 10 00 01 10 11 00 10 00 10 01 11 00 00 00 01 11 10 01 01 00 10 01 10 10 00 10 01 01 11 11 11 00 01 11 11 01 00 10 00 10 00 01 01 00 11 10 01 00 10 10 01 10 10 10 00 10 11 01 11 10 00"
]
for burst_str in burst_strs:

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

    sb_depunct = tetra_coding.depuncture_2_3(tetra_coding.hard_to_soft(sb_bits3))
    print_softbits("Depunctured:", sb_depunct)
    sb_bits2 = tetra_coding.decode_1_4(sb_depunct)
    print_bits("Type 2:", sb_bits2)

    sb_bits1 = sb_bits2[0:-16]
    print_bits("Type 1 (not CRC checked):", sb_bits1)
    print_bits("Received   CRC:", sb_bits2[-16:])
    print_bits("Calculated CRC:", tetra_coding.crc16(sb_bits1))

"""
# Speedtest
N = 10000

import time
t1 = time.time()

for i in range(N):
    sb_bits5 = burst[94:214]
    sb_bits4 = tetra_coding.descramble(sb_bits5, tetra_coding.sb_scrambling)
    sb_bits3 = tetra_coding.deinterleave(sb_bits4, 11)
    sb_depunct = tetra_coding.depuncture_2_3(tetra_coding.hard_to_soft(sb_bits3))
    sb_bits2 = tetra_coding.decode_1_4(sb_depunct)

t2 = time.time()
print("Descrambled, deinterleaved and decoded %f blocks per second" % (N / (t2-t1)))
"""
