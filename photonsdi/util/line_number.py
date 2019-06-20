from migen import *
from photonsdi.constants import *
from photonsdi.util.encdec import *


class SdiLineNumberEncoder(Module):
    def __init__(self):
        self.i_line_number = Signal(SDI_LINE_NUMBER_WIDTH)
        self.o_data = Signal(2 * SDI_ELEMENTARY_STREAM_DATA_WIDTH)  # first data word in LSBs

        ###

        self.submodules.enc9_0 += Sdi9BitEncoder()
        self.submodules.enc9_1 += Sdi9BitEncoder()

        self.comb += [
            self.enc9_0.i_data.eq(Cat(Replicate(0, 2), self.i_line_number[:7])),
            self.enc9_0.i_data.eq(Cat(Replicate(0, 2), self.i_line_number[7:], Replicate(0, 3))),
            self.o_data.eq(Cat(self.enc9_0.o_data, self.enc9_1.o_data))
        ]


class SdiLineNumberDecoder(Module):
    def __init__(self):
        self.i_data = Signal(2 * SDI_ELEMENTARY_STREAM_DATA_WIDTH)  # first data word in LSBs
        self.o_line_number = Signal(SDI_LINE_NUMBER_WIDTH)
        self.o_valid = Signal()

        ###

        self.submodules.dec9_0 += Sdi9BitDecoder()
        self.submodules.dec9_1 += Sdi9BitDecoder()

        self.comb += [
            self.dec9_0.i_data.eq(self.i_data[:SDI_ELEMENTARY_STREAM_DATA_WIDTH]),
            self.dec9_1.i_data.eq(self.i_data[SDI_ELEMENTARY_STREAM_DATA_WIDTH:]),
            self.o_line_number.eq(Cat(self.dec9_0.o_data[2:9], self.dec9_1.o_data[2:6])),
            self.o_valid.eq(self.dec9_0.o_valid and self.dec9_1.o_valid)
        ]
