from operator import xor

from migen import *
from photonsdi.constants import *


class SdiLfsrScrambler(Module):
    def __init__(self, lfsr_taps, datapath_width = 2 * SDI_ELEMENTARY_STREAM_DATA_WIDTH):
        assert lfsr_taps
        lfsr_length = max(lfsr_taps)

        self.i_data = Signal(datapath_width)
        self.o_data = Signal(datapath_width)
        self.i_last_state = Signal(lfsr_length)
        self.o_state = Signal(lfsr_length)

        ###

        feedback_taps = lfsr_taps[:]
        feedback_taps.remove(max(feedback_taps))

        state = [self.i_last_state[i] for i in range(lfsr_length)]

        for i in range(datapath_width):
            state.append(reduce(xor, [state[tap] for tap in feedback_taps] + [self.i_data[i]]))
            self.comb += [
                self.o_state[i].eq(state.pop(0))
            ]

        self.comb += [
            self.o_state.eq(Cat(*state[:lfsr_length]))
        ]


class Scrambler(Module):
    def __init__(self, elementary_stream_count = 2):
        assert elementary_stream_count in [2]
        datapath_width = elementary_stream_count * SDI_ELEMENTARY_STREAM_DATA_WIDTH

        self.i_data = Signal(datapath_width)
        self.o_data = Signal(datapath_width)

        ###

        scrambler_out = Signal(datapath_width)

        self.submodules.scrambler = SdiLfsrScrambler(SDI_SCRAMBLER_TAPS, datapath_width)

        self.comb += [
            self.scrambler.input.eq(self.i_data)
        ]
        self.sync += [
            scrambler_out.eq(self.scrambler.o_data),
            self.scrambler.i_last_state.eq(self.scrambler.o_state)
        ]

        self.submodules.nrzi = SdiLfsrScrambler(SDI_NRZI_TAPS, datapath_width)

        self.comb += [
            self.nrzi.input.eq(scrambler_out)
        ]
        self.sync += [
            self.o_data.eq(self.nrzi.o_data),
            self.nrzi.i_last_state.eq(self.nrzi.o_state)
        ]
