#!/usr/bin/env python3
"""Definitions of the PDU structures."""

# PDU contents are defined as tuples of tuples, containing:
# * Name of the information element, used as a name of a class member
# * Length in bits
# * Data type
# * Default value
# * Bool which is True in case the value is constant, that is,
#   should always have the default value for the PDU to be valid

pdus = {
# DMAC-SYNC PDU contents in SCH/S (ETSI EN 300 396-3)
"DMAC_SYNC_SCH_S": (
    ("System_code",            4, "int",  0, False),
    ("SYNC_PDU_type",          2, "int",  0, True),
    ("Communication_type",     2, "int",  0, False), # or should it be constant?
    ("Master_slave_link_flag", 1, "int",  0, False),
    ("Gateway_generated_flag", 1, "int",  0, False),
    ("A_B_channel_usage",      2, "int",  0, False),
    ("Slot_number",            2, "int",  0, False),
    ("Frame_number",           5, "int",  0, False),
    ("Encryption_state",       2, "int",  0, False),
    ("Reserved",              39, "int",  0, False) # For encryption
),
}
