from migen import *
from photonsdi.constants import *
from photonsdi.util.timing import *
from photonsdi.util.hamming import *


# (7, 3) code:
_generator_matrix = [
    [1, 0, 0, 1, 0, 1, 1],
    [0, 1, 0, 1, 1, 0, 1],
    [0, 0, 1, 1, 1, 1, 0]
]


class SdiXyzEncoder(Module):
    def __init__(self):
        self.i_timing_flags = Record(SDI_TIMING_FLAGS)
        self.o_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)

        ###

        self.submodules.hamming_calc = HammingEncoder(_generator_matrix)

        self.comb += [
            self.hamming_calc.i_data.eq(Cat(self.i_timing_flags.h,
                                            self.i_timing_flags.v,
                                            self.i_timing_flags.f)),
            self.o_data.eq(Cat(Replicate(0, 2),
                               self.hamming_calc.o_data[len(_generator_matrix):],
                               self.hamming_calc.o_data[:len(_generator_matrix)],
                               1))
        ]


class SdiXyzDecoder(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.o_timing_flags = Record(SDI_TIMING_FLAGS)
        self.o_corrected = Signal()

        ###

        self.submodules.hamming_dec = HammingDecoder(_generator_matrix)

        self.comb += [
            self.hamming_dec.i_data.eq(Cat(self.i_data[6:9], self.i_data[2:6])),

            self.o_timing_flags.h.eq(self.hamming_dec.o_data[0]),
            self.o_timing_flags.v.eq(self.hamming_dec.o_data[1]),
            self.o_timing_flags.f.eq(self.hamming_dec.o_data[2]),

            self.o.corrected.eq(self.hamming_dec.o_corrected)
        ]
