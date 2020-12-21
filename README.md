# AMTETRA 2

This is our second attempt to implement a protocol stack for Terrestrial
Trunked Radio (TETRA).

## Software design

Most of this is not implemented yet.

### L1 and L2

Layer 1 and layer 2 run in a single thread, whose main loop does this:

* Reads a buffer of samples from a radio receiver
  * This is where the thread blocks until the next buffer is available.
* Demodulates those samples (L1)
* Does L2 things
  * When L1 has detected a burst, it calls L2 to pass the demodulated
    burst to it.
* Produces transmit samples (L1)
  * When L1 is ready to modulate the next transmit burst, it calls L2
    to request a burst of to be transmitted.
* Writes a buffer of samples to a radio transmitter
  * Timestamp of the transmit buffer is given a fixed offset relative to the
    latest received buffer, maintaining a controlled round-trip latency.

This approach was previously found to work well.
Transmit samples are produced some 10-20 ms before transmission, so scheduling
latencies of a couple of milliseconds are tolerated.

It can be considered soft-real time: if the loop gets too late to produce
transmit samples in time, the radio transmitter will get a buffer with a
timestamp in the past, and should just skip transmitting that buffer.
This results in a gap in the transmitted signal, but radio systems have to
deal with occassional bit errors anyway. In practice, with careful choice of
parameters, such deadline misses were found to occur fairly rarely even on a
normal desktop Linux system and a USB-connected LimeSDR.

### L3

Layer 3 runs in a separate process, and communicates with L2 through
some IPC mechanism such as a ZeroMQ socket.

### Choice of language

This time, most of the code will be written in Python 3, which will hopefully
make experimentation and further development easier compared to the first
version written in C. This also serves as an experiment on implementing a
complete protocol stack in a high level language, and we are not entirely
sure yet whether it's actually a good idea or not.

Some performance-critical parts may be written in other languages, and
libraries written in other languages may be used in case a suitable Python
library can't be found. For example, decoding of convolutional codes is
currently done by calling [libcorrect](https://github.com/quiet/libcorrect)
using ctypes.

## Goals

After basic decoding, encoding, demodulation and modulation of TETRA bursts
is working, the next goal is to implement a direct mode repeater (DM-REP)
and later extend it to appear as a gateway (DM-GATE).
