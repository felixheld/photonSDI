# part of this code is borrowed from https://lab.whitequark.org/notes/2016-10-18/implementing-an-uart-in-verilog-and-migen/

# for this test to work on the board, you need to apply axiom_photonsdi_hw.patch

from migen import *
from photonsdi.boards.platforms import axiom_photonsdi_hw


class BaudrateGenerator(Module):
    def __init__(self, clkin, baudrate):
        self.baud_strobe = Signal()

        def _uart_divisor(sysclk, baudrate):
            return int((sysclk + baudrate / 2) // baudrate)

        divisor = _uart_divisor(clkin, baudrate)
        baud_cntr = Signal(max = divisor)
        self.sync += [
            If(0 == baud_cntr,
                baud_cntr.eq(divisor - 1),
                self.baud_strobe.eq(1)
            ).Else(
                baud_cntr.eq(baud_cntr - 1),
                self.baud_strobe.eq(0)
            )
        ]


class UARTTXConst(Module):
    def __init__(self, data, i_tx_baud_strobe, tx_start, o_tx):

        tx_number_of_bits = 8
        tx_shiftreg = Signal(tx_number_of_bits)
        tx_bitnumber = Signal(max=tx_number_of_bits)

        self.submodules.tx_fsm = FSM(reset_state="IDLE")
        self.tx_fsm.act("IDLE",
            NextValue(o_tx, 1),
            If(i_tx_baud_strobe,
                If(tx_start,
                    NextValue(tx_shiftreg, data),
                    NextState("START")
                )
            )
        )
        self.tx_fsm.act("START",
            If(i_tx_baud_strobe,
                NextState("DATA"),
                NextValue(o_tx, 0),
                NextValue(tx_bitnumber, 0)
            )
        )
        self.tx_fsm.act("DATA",
            If(i_tx_baud_strobe,
                NextValue(o_tx, tx_shiftreg[0]),
                NextValue(tx_shiftreg, Cat(tx_shiftreg[1:8], 0)),  # would it be better to replace the 0 with a tx_shiftreg[0]?
                NextValue(tx_bitnumber, tx_bitnumber + 1),
                If(tx_bitnumber == tx_number_of_bits - 1,
                    NextState("STOP")
                )
            )
        )
        self.tx_fsm.act("STOP",
            If(i_tx_baud_strobe,
                NextState("IDLE"),
                NextValue(o_tx, 1)
            )
        )


class MultiUARTTXConst(Module):
    def __init__(self, sys_clk_freq, baud_rate, channel_count, offset):
        self.tx = Signal(channel_count)

        self.submodules.baudrate_generator = BaudrateGenerator(sys_clk_freq, baud_rate)

        tx_data = Signal(channel_count)
        tx_oe = Signal(channel_count)
        tx_start = Signal()

        bit_times_between_tx_begins = 16
        bit_time_counter = Signal(max=bit_times_between_tx_begins)

        active_output_number = Signal(max=channel_count)

        self.sync += [
            tx_oe.eq(1 << active_output_number),
            If(self.baudrate_generator.baud_strobe,
                If(0 == bit_time_counter,
                    bit_time_counter.eq(bit_times_between_tx_begins - 1),
                    tx_start.eq(1),
                    If(0 == active_output_number,
                        active_output_number.eq(channel_count - 1)
                    ).Else(
                        active_output_number.eq(active_output_number - 1)
                    )
                ).Else(
                    bit_time_counter.eq(bit_time_counter - 1),
                    tx_start.eq(0)
                )
            )
        ]

        for i in range(channel_count):
            self.submodules += UARTTXConst(offset + i, self.baudrate_generator.baud_strobe, tx_start, tx_data[i])
            t = TSTriple()
            self.comb += [
                t.o.eq(tx_data[i]),
                t.oe.eq(tx_oe[i])
            ]
            self.specials += t.get_tristate(self.tx[i])


class Iotest(Module):
    def __init__(self, platform):
        clk_freq = int((1 / (platform.default_clk_period)) * 1000000000)

        serial = platform.request("serial")
        aux1 = platform.request("aux")
        aux2 = platform.request("aux")
        axiom_data = platform.request("axiom_data")

        _list_of_pins = [
            serial.tx,
            serial.rx,
            aux1,
            aux2,
            axiom_data.n0p,
            axiom_data.n0n,
            axiom_data.n1p,
            axiom_data.n1n,
            axiom_data.n2p,
            axiom_data.n2n,
            axiom_data.n3p,
            axiom_data.n3n,
            axiom_data.n4p,
            axiom_data.n4n,
            axiom_data.n5p,
            axiom_data.n5n,
            axiom_data.s0p,
            axiom_data.s0n,
            axiom_data.s1p,
            axiom_data.s1n,
            axiom_data.s2p,
            axiom_data.s2n,
            axiom_data.s3p, # swapped
            axiom_data.s3n, # swapped
            axiom_data.s4p, # swapped
            axiom_data.s4n, # swapped
            axiom_data.s5p, # swapped
            axiom_data.s5n, # swapped
        ]

        output_count = len(_list_of_pins)

        self.submodules.test_signal_generator = MultiUARTTXConst(clk_freq, 115200, output_count, 0x20)

        for i in range(output_count):
            self.comb += _list_of_pins[i].eq(self.test_signal_generator.tx[i])


def main():
    platform = axiom_photonsdi_hw.Platform()
    dut = Iotest(platform)
    platform.build(dut)


if __name__ == "__main__":
    main()
