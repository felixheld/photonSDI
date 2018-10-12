#!/usr/bin/env python3

from litex.build.generic_platform import *

_io = [
    ("clk25", 0, Pins("C18"), IOStandard("LVCMOS18")),

    ("user_led", 0, Pins("E21"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("E22"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("G21"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("G22"), IOStandard("LVCMOS18")),

    ("spiflash_4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq", Pins("P22", "R22", "P21", "R21")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash_1x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp", Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33")
    ),

    ("serial", 0,
        Subsignal("tx", Pins("AA19")),
        Subsignal("rx", Pins("AB20")),
        IOStandard("LVCMOS33")
    ),

    ("aux", 0, Pins("AB18"), IOStandard("LVCMOS33")),
    ("aux", 1, Pins("AA18"), IOStandard("LVCMOS33")),

    # main data connection to the axiom beta
    ("axiom_data", 0,
        Subsignal("n0p", Pins("N18")),
        Subsignal("n0n", Pins("N19")),
        Subsignal("n1p", Pins("N22")),
        Subsignal("n1n", Pins("M22")),
        Subsignal("n2p", Pins("N20")),
        Subsignal("n2n", Pins("M20")),
        Subsignal("n3p", Pins("K18")),
        Subsignal("n3n", Pins("K19")),
        Subsignal("n4p", Pins("J19")),
        Subsignal("n4n", Pins("H19")),
        Subsignal("n5p", Pins("J22")),
        Subsignal("n5n", Pins("H22")),
        Subsignal("s0p", Pins("T1")),
        Subsignal("s0n", Pins("U1")),
        Subsignal("s1p", Pins("W1")),
        Subsignal("s1n", Pins("Y1")),
        Subsignal("s2p", Pins("AA1")),
        Subsignal("s2n", Pins("AB1")),
        Subsignal("s3p", Pins("AB3")),  # swapped
        Subsignal("s3n", Pins("AB2")),  # swapped
        Subsignal("s4p", Pins("V4")),   # swapped
        Subsignal("s4n", Pins("W4")),   # swapped
        Subsignal("s5p", Pins("AB7")),  # swapped
        Subsignal("s5n", Pins("AB6")),  # swapped
        IOStandard("LVDS_25"),
        Misc("DIFF_TERM=TRUE"),
    ),

    ("sync_in", 0,
        Subsignal("hsync", Pins("F3")),
        Subsignal("vsync", Pins("G1")),
        Subsignal("odd_even", Pins("F1")),
        Subsignal("vformat", Pins("G2")),
        IOStandard("LVCMOS18")
    ),

    # GTP reference clock from si534x
    ("sdi_refclk", 0,
        Subsignal("p", Pins("F6")), # swapped
        Subsignal("n", Pins("E6")), # swapped
    ),
    # clock feedback path from FPGA to si534x
    ("sdi_refclk_fbout", 0,
        Subsignal("p", Pins("R1")),
        Subsignal("n", Pins("P1")),
        IOStandard("LVCMOS18")
    ),
    ("si534x_spi", 0,
        Subsignal("clk", Pins("M1")),
        Subsignal("cs_n", Pins("L1")),
        Subsignal("mosi", Pins("N2")),
        Subsignal("miso", Pins("M2")),
        IOStandard("LVCMOS18")
    ),
    ("si534x_ctl", 0,
        Subsignal("rst_n", Pins("M3")),
        Subsignal("oe_n", Pins("P4")),
        Subsignal("lol_n", Pins("L3")),
        Subsignal("irq_n", Pins("K3")),
        IOStandard("LVCMOS18")
    ),

    ("sdi_out", 0,
        Subsignal("p", Pins("B4")),
        Subsignal("n", Pins("A4")),
    ),
    ("sdi_out_spi", 0,
        Subsignal("clk", Pins("B1")),
        Subsignal("cs_n", Pins("E1")),
        Subsignal("mosi", Pins("E2")),
        Subsignal("miso", Pins("D1")),
        IOStandard("LVCMOS18")
    ),
    ("sdi_out_gpio", 0,
        Subsignal("gpio0", Pins("B2")),
        Subsignal("gpio1", Pins("A1")),
        IOStandard("LVCMOS18")
    ),

    ("sdi_out", 1,
        Subsignal("p", Pins("B6")),
        Subsignal("n", Pins("A6")),
    ),
    ("sdi_out_spi", 1,
        Subsignal("clk", Pins("C20")),
        Subsignal("cs_n", Pins("A18")),
        Subsignal("mosi", Pins("B18")),
        Subsignal("miso", Pins("A19")),
        IOStandard("LVCMOS18")
    ),
    ("sdi_out_gpio", 1,
        Subsignal("gpio0", Pins("D20")),
        Subsignal("gpio1", Pins("D21")),
        IOStandard("LVCMOS18")
    ),

    ("sdi_in", 0,
        Subsignal("p", Pins("B8")),
        Subsignal("n", Pins("A8")),
    ),
    ("sdi_in_spi", 0,
        Subsignal("clk", Pins("B21")),
        Subsignal("cs_n", Pins("A20")),
        Subsignal("mosi", Pins("B20")),
        Subsignal("miso", Pins("A21")),
        IOStandard("LVCMOS18")
    ),
    ("sdi_in_gpio", 0,
        Subsignal("gpio0", Pins("C22")),
        Subsignal("gpio1", Pins("D22")),
        IOStandard("LVCMOS18")
    ),
]

