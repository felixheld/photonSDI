from collections import OrderedDict
from operator import xor

from migen import *
from photonsdi.constants import *


class SdiCrcEngine(Module):
    """Cyclic Redundancy Check Engine

    Compute next CRC value from last CRC value and data input using
    an optimized asynchronous LFSR.

    Parameters
    ----------
    data_width : int
        Width of the data bus.
    taps : list
        list of all LFSR taps, including the first and last
        this implicitly specifies the number of bits of the internal state

    Attributes
    ----------
    data : in
        Data input.
    last_crc : in
        last CRC value.
    crc_out :
        next CRC value.
    """
    def __init__(self, data_width, taps):
        state_width = max(taps)

        self.data = Signal(data_width)
        self.last_crc = Signal(state_width)
        self.crc_out = Signal(state_width)

        ###

        def _optimize_eq(l):
            """
            remove an even numbers of XORs with the same bit
            replace an odd number of XORs with a single XOR
            """
            d = OrderedDict()
            for e in l:
                if e in d:
                    d[e] += 1
                else:
                    d[e] = 1
            r = []
            for key, value in d.items():
                if value%2 != 0:
                    r.append(key)
            return r

        # compute and optimize the parallel implementation of the CRC's LFSR
        # note: SDI counts the CRC state bits in reverse order compared to IEEE 802.3 CRC
        # ITU R-REC-BT.2077-0 says: "CRCC0 is the MSB of the error detection code."
        curval = [[("state", i)] for i in range(state_width)]
        curval.reverse()
        for i in range(data_width):
            feedback = curval.pop() + [("din", i)]
            for j in range(state_width - 1):
                if j + 1 in taps:
                    curval[j] += feedback
                curval[j] = _optimize_eq(curval[j])
            curval.insert(0, feedback)
        curval.reverse()

        # implement logic
        for i in range(state_width):
            xor_list = []
            for t, n in curval[i]:
                if t == "state":
                    xor_list += [self.last_crc[n]]
                elif t == "din":
                    xor_list += [self.data[n]]
            self.comb += self.crc_out[i].eq(reduce(xor, xor_list))


class SdiChannelCrc(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.i_clear = Signal()     # set next crc value to 0
        self.i_enable = Signal()    # use data at the clock cycle to calculate new crc
        self.o_crc = Signal(SDI_CRC_LENGTH) # output latency: 1 clock cycle

        ###

        self.submodules.crc_engine = SdiCrcEngine(SDI_ELEMENTARY_STREAM_DATA_WIDTH, SDI_CRC_TAPS)

        next_last_crc = Signal(SDI_CRC_LENGTH)

        self.sync += [
            If(self.i_clear,
                next_last_crc.eq(0)
            ).Else(
                If(self.i_enable,
                    next_last_crc.eq(self.crc_engine.crc_out)
                ).Else(
                    next_last_crc.eq(self.crc_engine.last_crc)
                )
            )
        ]

        self.comb += [
            self.crc_engine.data.eq(self.i_data),
            self.crc_engine.last_crc.eq(next_last_crc),
            self.o_crc.eq(next_last_crc)
        ]
