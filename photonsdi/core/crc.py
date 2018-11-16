from collections import OrderedDict
from operator import xor

from migen import *
from photonsdi.common import *


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
        width = max(taps)

        self.data = Signal(data_width)
        self.last_crc = Signal(width)
        self.crc_out = Signal(width)

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
        curval = [[("state", i)] for i in range(width)]
        curval.reverse()
        for i in range(data_width):
            feedback = curval.pop() + [("din", i)]
            for j in range(width - 1):
                if j + 1 in taps:
                    curval[j] += feedback
                curval[j] = _optimize_eq(curval[j])
            curval.insert(0, feedback)
        curval.reverse()

        # implement logic
        for i in range(width):
            xors = []
            for t, n in curval[i]:
                if t == "state":
                    xors += [self.last_crc[n]]
                elif t == "din":
                    xors += [self.data[n]]
            self.comb += self.crc_out[i].eq(reduce(xor, xors))


class SdiChannelCrc(Module):
    def __init__(self):
        self.i_data = Signal(SDI_ELEMENTARY_STREAM_DATA_WIDTH)
        self.i_clear = Signal
        self.i_enable = Signal
        self.o_crc = Signal(SDI_CRC_LENGTH) # output latency: 1 clock cycle

        ###

        self.submodules.crc_engine += SdiCrcEngine(SDI_ELEMENTARY_STREAM_DATA_WIDTH, SDI_CRC_TAPS)

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
