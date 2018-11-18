from migen import *
from photonsdi.constants import *


# when 9 bit values are encoded for the SDI stream, the inverted 9th bit is
# used as 10th bit so that the 10 bit value can't be outside the allowed data
# value range


class Sdi9BitEncoder(Module):
    def __init__(self):
        self.i_data = Signal(9)
        self.o_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)

        ###

        self.comb += [
            self.o_data.eq(Cat(self.i_data, ~self.i_data[8]))
        ]


class Sdi9BitDecoder(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.o_data = Signal(9)
        self.o_valid = Signal()

        ###

        self.comb += [
            self.o_data.eq(self.i_data[:9]),
            If(self.i_data[8] != self.i_data[9],
                self.o_valid.eq(1)
            ).Else(
                self.o_valid.eq(0)
            )
        ]
