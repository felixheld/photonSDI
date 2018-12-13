from migen import *
from photonsdi.constants import *
from photonsdi.util.lfsr import *


class SdiDescrambler(Module):
    def __init__(self, elementary_stream_count = 2):
        assert elementary_stream_count in [2]
        datapath_width = elementary_stream_count * SDI_ELEMENTARY_STREAM_DATA_WIDTH

        self.i_data = Signal(datapath_width)
        self.o_data = Signal(datapath_width)

        ###

        nrzi_output = Signal(datapath_width)

        self.submodules.nrzi = LfsrDescrambler(SDI_NRZI_TAPS, datapath_width)

        self.comb += [
            self.nrzi.i_data.eq(self.i_data)
        ]
        self.sync += [
            nrzi_output.eq(self.nrzi.o_data),
            self.nrzi.i_last_state.eq(self.nrzi.o_state)
        ]

        self.submodules.scrambler = LfsrDescrambler(SDI_SCRAMBLER_TAPS, datapath_width)

        self.comb += [
            self.scrambler.i_data.eq(nrzi_output)
        ]
        self.sync += [
            self.o_data.eq(self.scrambler.o_data),
            self.scrambler.i_last_state.eq(self.scrambler.o_state)
        ]
