from operator import xor

from migen import *
from photonsdi.constants import *
from photonsdi.util.encdec import *


class AncHeaderWordEncode(Module):
    def __init__(self):
        self.i_data = Signal(8)
        self.o_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)

        ###

        parity = reduce(xor, [self.i_data[i] for i in range(8)])

        self.submodules.enc9 += Sdi9BitEncode()

        self.comb += [
            self.enc9.i_data.eq(Cat(self.i_data, parity)),
            self.o_data.eq(self.enc9.o_data)
        ]


class AncHeaderWordDecode(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.o_data = Signal(8)
        self.o_valid = Signal()

        ###

        self.submodules.dec9 += Sdi9BitDecode()

        parity = reduce(xor, [self.dec9.o_data[i] for i in range(8)])

        self.comb += [
            self.dec9.i_data.eq(self.i_data),
            self.o_data.eq(self.dec9.o_data[:8]),
            If(self.dec9.o_valid and self.self.dec9.o_data[8] == parity,
                self.o_valid.eq(1)
            ).Else(
                self.o_valid.eq(0)
            )
        ]
