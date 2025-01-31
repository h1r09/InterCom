#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

''' Real-time Audio Intercommunicator (compress3.py). '''

import zlib
import numpy as np
import struct
import math
import minimal
import compress

class Compression4(compress.Compression):
    '''Compress the chunks by byte-planes ([MSB], [LSB]), where the frames
are interlaced [frame0, frame1]). Each byte-plane is compressed
independently.

    '''
    def __init__(self):
        if __debug__:
            print("Running Compression4.__init__")
        super().__init__()

    def pack(self, chunk_number, chunk):
        MSB = (chunk // 256).astype(np.int8)
        LSB = (chunk % 256).astype(np.uint8)
        compressed_MSB = zlib.compress(MSB)
        compressed_LSB = zlib.compress(LSB)
        packed_chunk = struct.pack("!HH", chunk_number, len(compressed_MSB)) + compressed_MSB + compressed_LSB 
        return packed_chunk

    def unpack(self, packed_chunk):
        (chunk_number, len_compressed_MSB) = struct.unpack("!HH", packed_chunk[:4])
        compressed_MSB = packed_chunk[4:len_compressed_MSB+4]
        compressed_LSB = packed_chunk[len_compressed_MSB+4:]
        MSB = np.frombuffer(zlib.decompress(compressed_MSB), dtype=np.int8).reshape((minimal.args.frames_per_chunk, 2))
        LSB = np.frombuffer(zlib.decompress(compressed_LSB), dtype=np.uint8).reshape((minimal.args.frames_per_chunk, 2))
        chunk = MSB*256 + LSB
        return chunk_number, chunk

class Compression4__verbose(Compression4, compress.Compression__verbose):
    def __init__(self):
        if __debug__:
            print("Running Compression4__verbose.__init__")
        super().__init__()

    def unpack(self, packed_chunk):
        (chunk_number, len_compressed_channel_0) = struct.unpack("!HH", packed_chunk[:4])
        len_compressed_channel_1 = len(packed_chunk[len_compressed_channel_0+4:])

        self.bps[0] += len_compressed_channel_0*8
        self.bps[1] += len_compressed_channel_1*8
        return Compression4.unpack(self, packed_chunk)

try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    logging.warning("Unable to import argcomplete (optional)")

if __name__ == "__main__":
    minimal.parser.description = __doc__
    try:
        argcomplete.autocomplete(minimal.parser)
    except Exception:
        logging.warning("argcomplete not working :-/")
    minimal.args = minimal.parser.parse_known_args()[0]
    if minimal.args.show_stats or minimal.args.show_samples:
        intercom = Compression4__verbose()
    else:
        intercom = Compression4()
    try:
        intercom.run()
    except KeyboardInterrupt:
        minimal.parser.exit("\nInterrupted by user")
