from operator import xor

from migen import *
from photonsdi.constants import *


class AncHeaderWordEncode(Module):
    def __init__(self):
        self.i_data = Signal(8)
        self.o_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)

        ###

        parity = reduce(xor, [self.i_data[i] for i in range(8)])
        self.comb += [
            self.o_data.eq(Cat(self.i_data, parity, ~parity))
        ]


class AncHeaderWordDecode(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.o_data = Signal(8)
        self.o_valid = Signal()

        ###

        parity = reduce(xor, [self.i_data[i] for i in range(8)])
        self.comb += [
            self.o_data.eq(self.i_data[:8]),
            If(self.i_data[8] == parity and self.i_data[9] == ~parity,
                self.o_valid.eq(1)
            ).Else(
                self.o_valid.eq(0)
            )
        ]
