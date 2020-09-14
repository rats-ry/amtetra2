# HamTETRA 2

This is our second attempt to implement a protocol stack for Terrestrial
Trunked Radio (TETRA).

This time, most of the code will be written in Python 3, which will hopefully
make experimentation and further development easier compared to the first
version written in C. This also serves as an experiment on implementing a
complete protocol stack in a high level language, and we are not entirely
sure yet whether it's actually a good idea or not.

After basic decoding, encoding, demodulation and modulation of TETRA bursts
is working, the next goal is to implement a direct mode repeater (DM-REP)
and later extend it to appear as a gateway (DM-GATE).
