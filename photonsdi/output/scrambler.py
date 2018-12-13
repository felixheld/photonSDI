from migen import *
from photonsdi.constants import *
from photonsdi.util.lfsr import *


class SdiScrambler(Module):
    def __init__(self, elementary_stream_count = 2):
        assert elementary_stream_count in [2]
        datapath_width = elementary_stream_count * SDI_ELEMENTARY_STREAM_DATA_WIDTH

        self.i_data = Signal(datapath_width)
        self.o_data = Signal(datapath_width)

        ###

        scrambler_out = Signal(datapath_width)

        self.submodules.scrambler = LfsrScrambler(SDI_SCRAMBLER_TAPS, datapath_width)

        self.comb += [
            self.scrambler.input.eq(self.i_data)
        ]
        self.sync += [
            scrambler_out.eq(self.scrambler.o_data),
            self.scrambler.i_last_state.eq(self.scrambler.o_state)
        ]

        self.submodules.nrzi = LfsrScrambler(SDI_NRZI_TAPS, datapath_width)

        self.comb += [
            self.nrzi.input.eq(scrambler_out)
        ]
        self.sync += [
            self.o_data.eq(self.nrzi.o_data),
            self.nrzi.i_last_state.eq(self.nrzi.o_state)
        ]
