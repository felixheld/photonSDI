from operator import xor

from migen import *
from photonsdi.constants import *
from photonsdi.util.timing import *


# (7, 3) code:
_generator_matrix = [
    [1, 0, 0, 1, 0, 1, 1],
    [0, 1, 0, 1, 1, 0, 1],
    [0, 0, 1, 1, 1, 1, 0]
]


class SdiXwzProtectionBitCalc(Module):
    def __init__(self):
        self.i_timing_flags = Record(SDI_TIMING_FLAGS)
        self.o_protection_bits = Signal(4)

        ###

        self.comb += [
            self.o_protection_bits[0].eq(self.i_timing_flags.h xor
                                         self.i_timing_flags.v xor
                                         self.i_timing_flags.f),
            self.o_protection_bits[1].eq(self.i_timing_flags.v xor
                                         self.i_timing_flags.f),
            self.o_protection_bits[2].eq(self.i_timing_flags.h xor
                                         self.i_timing_flags.f),
            self.o_protection_bits[3].eq(self.i_timing_flags.h xor
                                         self.i_timing_flags.v),
        ]


class SdiXyzEncoder(Module):
    def __init__(self):
        self.i_timing_flags = Record(SDI_TIMING_FLAGS)
        self.o_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)

        ###

        protection_bits = Signal(4)

        self.submodules.protection_bit_calc += SdiXwzProtectionBitCalc()

        self.comb += [
            self.protection_bit_calc.i_timing_flags.eq(self.i_timing_flags),
            protection_bits.eq(self.protection_bit_calc.o_protection_bits),
            self.o_data.eq(Cat(Replicate(0, 2),
                               protection_bits,
                               self.i_timing_flags.h,
                               self.i_timing_flags.v,
                               self.i_timing_flags.f,
                               1))
        ]


class SdiXyzDecoder(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.o_timing_flags = Record(SDI_TIMING_FLAGS)
        # TODO: signal detected and corrected bit errors

        ###

        timing_flags = Record(SDI_TIMING_FLAGS)
        received_protection_bits = Signal(4)
        calculated_protection_bits = Signal(4)

        self.submodules.protection_bit_calc += SdiXwzProtectionBitCalc()

        self.comb += [
            received_protection_bits.eq(self.i_data[2:6]),
            timing_flags.h.eq(self.i_data[6]),
            timing_flags.v.eq(self.i_data[7]),
            timing_flags.f.eq(self.i_data[8]),

            self.protection_bit_calc.i_timing_flags.eq(timing_flags),
            calculated_protection_bits.eq(self.protection_bit_calc.o_protection_bits),

            If(received_protection_bits == calculated_protection_bits,
                self.o_timing_flags.eq(timing_flags)
            ).Else(
                # TODO: implement error detection/correction
            )
        ]
