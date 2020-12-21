#!/usr/bin/env python3
"""Functions used to show debugging and diagnostic information
for development, testing and monitoring purposes"""

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

def print_dict(d):
    for key, val in d.items():
        print("%30s: %30s" % (key, val))
