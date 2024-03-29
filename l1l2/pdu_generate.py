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
    # TODO: Check the constant fields (if that feature is actually needed).

    spec_code    = ""  # Numba spec
    default_code = ""  # Code to initialize default values
    unpack_code  = ""  # Code to unpack PDU from bits to elements
    pack_code    = ""  # Code to pack PDU to bits
    list_code    = ""  # Code to return elements as a list

    n = 0  # Position within the PDU
    for el_name, el_len, el_type, el_default, el_const in elements:
        spec_code += f"    ('{el_name}', numba.uint32),\n"

        default_code += f"            self.{el_name} = {el_default}\n"

        unpack_code += \
            "            self.%s = _bits_to_int(bits[%d:%d])\n" % \
            (el_name, n, n + el_len)

        pack_code += \
            "        _int_to_bits(self.%s, bits[%d:%d])\n" % \
            (el_name, n, n + el_len)

        list_code += f"            ('{el_name}', self.{el_name}),\n"

        n += el_len

    # n is the total number of bits now
    return f"""
@jitclass([
{spec_code}])
class {pdu_name}:
    def __init__(self, bits = None):
        if bits is None: # initialize with default values
{default_code}
        else: # unpack from bits
            if bits.shape[0] != {n}:
                raise ValueError("{pdu_name} should have {n} bits")
{unpack_code}
    def bits(self):
        bits = np.zeros({n}, dtype=np.uint8)
{pack_code}
        return bits

    def list(self):
        return [
{list_code}        ]
"""


def main():
    with open("pdu_class.py", "w") as f:
        f.write(code_header)
        for pdu_name, pdu_elements in pdu_definition.pdus.items():
            f.write(pdu_class_code(pdu_name, pdu_elements))


if __name__ == "__main__":
    main()
