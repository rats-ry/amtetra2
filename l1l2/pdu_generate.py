#!/usr/bin/env python3
"""Generate the code for classes handling PDUs."""

import pdu_definition

code_header = """#!/usr/bin/env python3
\"\"\"Classes to handle PDUs.

This code is generated by pdu_generate.py
based on pdu_definition.py.\"\"\"

import numpy as np
import numba
try:
    from numba.experimental import jitclass
except ImportError:
    from numba import jitclass

@numba.njit()
def _bits_to_int(bits):
    v = 0
    for b in bits:
        v <<= 1
        v |= b
    return v

@numba.njit()
def _int_to_bits(v, bits):
    for i in range(len(bits)-1, -1, -1):
        bits[i] = v & 1
        v >>= 1
"""

def pdu_class_code(pdu_name, elements):
    """Generate the code for a PDU class."""
    # TODO: Support other data types (if they are actually needed).
    # TODO: Check the length of a PDU before unpacking.
    # TODO: Check the constant fields (if that feature is actually needed).

    code = "\n@jitclass([\n" + \
        "".join("    ('%s', numba.uint32),\n" % el_name \
            for el_name, _, _, _, _ in elements) + \
        "])\nclass %s:\n" % pdu_name + \
        "    def __init__(self, bits = None):\n" + \
        "        if bits is None: # initialize with default values\n" + \
        "".join("            self.%s = %s\n" % (el_name, el_default) \
            for el_name, _, _, el_default, _ in elements) + \
        "        else: # unpack from bits\n"

    n = 0  # Position within the PDU
    for el_name, el_len, el_type, el_default, el_const in elements:
        code += "            self.%s = _bits_to_int(bits[%d:%d])\n" % \
            (el_name, n, n + el_len)
        n += el_len

    # n is the total number of bits now
    code += "    def bits(self):\n"
    code += "        bits = np.zeros(%d, dtype=np.uint8)\n" % n

    n = 0  # Position within the PDU
    for el_name, el_len, el_type, el_default, el_const in elements:
        code += "        _int_to_bits(self.%s, bits[%d:%d])\n" % \
            (el_name, n, n + el_len)
        n += el_len

    code += "        return bits\n"
    return code


def main():
    with open("pdu_class.py", "w") as f:
        f.write(code_header)
        for pdu_name, pdu_elements in pdu_definition.pdus.items():
            f.write(pdu_class_code(pdu_name, pdu_elements))


if __name__ == "__main__":
    main()