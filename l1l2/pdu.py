#!/usr/bin/env python3
"""Functions to parse and create various types of PDUs"""

import numpy as np
import numba

def _zerobits(n):
    return np.zeros(n, dtype=np.uint8)

# PDU contents are defined as tuples of tuples, containing:
# * Name of the information element, used as a dictionary key
# * Length in bits
# * Data type
# * Default value
# * Bool which is True in case the value is constant, that is,
#   should always have the default value for the PDU to be valid

# DMAC-SYNC PDU contents in SCH/S (ETSI EN 300 396-3)
DMAC_SYNC_SCH_S = (
    ("System code",            4, "int",  0, False),
    ("SYNC PDU type",          2, "int",  0, True),
    ("Communication type",     2, "int",  0, False), # or should it be constant?
    ("Master/slave link flag", 1, "int",  0, False),
    ("Gateway generated flag", 1, "int",  0, False),
    ("A/B channel usage",      2, "int",  0, False),
    ("Slot number",            2, "int",  0, False),
    ("Frame number",           5, "int",  0, False),
    ("Encryption state",       2, "int",  0, False),
    ("Reserved",              39, "bit", _zerobits(39), False) # For encryption
)

@numba.njit()
def _bits_to_int(bits):
    v = 0
    for b in bits:
        v <<= 1
        v |= b
    return v

# Functions to convert bit array into another type
_bits_to_type = {
    "bit"  : lambda x: x,
    "byte" : lambda x: np.packbits(x),
    # There might be a simpler way to do this conversion...
    "int"  : _bits_to_int,
}

def unpack(bits, contents):
    """Unpack fields from PDU bits into a dictionary"""
    d = {}
    n = 0
    valid = True
    for c in contents:
        value = _bits_to_type[c[2]](bits[n : n + c[1]])
        d[c[0]] = value
        if c[4] and value != c[3]:
            valid = False
        n += c[1]
    d["valid"] = valid
    return d

def pack(d, contents):
    """Pack fields from a dictionary into PDU bits"""
    # TODO
    for c in contents:
        pass

