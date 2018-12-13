from operator import xor

from migen import *


class LfsrScrambler(Module):
    def __init__(self, lfsr_taps, datapath_width):
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


class LfsrDescrambler(Module):
    def __init__(self, lfsr_taps, datapath_width):
        assert lfsr_taps
        lfsr_length = max(lfsr_taps)

        self.i_data = Signal(datapath_width)
        self.o_data = Signal(datapath_width)
        self.i_last_state = Signal(lfsr_length)
        self.o_state = Signal(lfsr_length)

        ###

        curval = Cat(self.i_last_state, self.i_data)

        for i in range(datapath_width):
            self.comb += [
                self.o_data[i].eq(reduce(xor, [curval[tap + i] for tap in lfsr_taps]))
            ]

        self.comb += [
            self.o_state.eq(self.i_data[-lfsr_length:])
        ]
