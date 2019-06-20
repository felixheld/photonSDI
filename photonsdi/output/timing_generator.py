# parts of this code are inspired from the litevideo output core

from migen import *
from litex.soc.interconnect import stream
from photonsdi.constants import *
from photonsdi.util.timing import *


class SdiTimingGenerator(Module):
    def __init__(self, genlock_stream = None):
        # TODO: probably some stream handshaking signal generation missing
        self.sink = sink = stream.Endpoint(SDI_TIMING_PARAMETERS)  # module input
        self.source = source = stream.Endpoint(SDI_TIMING)  # module output

        ###

        if genlock_stream is None:
            # the pipeline steps are counted in reverse, so we can use this numbers for the array ranges
            PIPELINE_H_GEN_STEP  = 3
            PIPELINE_V_GEN_STEP  = 2
            PIPELINE_TIMING_STEP = 1
            PIPELINE_FINAL_STEP  = 0

            h_counter = Array(Signal(SDI_LINE_LENGTH_WIDTH) for _ in range(PIPELINE_H_GEN_STEP + 1))
            v_counter = Array(Signal(SDI_LINE_NUMBER_WIDTH) for _ in range(PIPELINE_V_GEN_STEP + 1))

            h_active = Signal()
            v_active = Signal()
            field = Signal()
            begin_sav = Signal()
            begin_eav = Signal()

            h_begin_sav_pos = Signal()
            h_begin_eav_pos = Signal()

            # SAV is the last 4 words before the active video that starts at 0
            self.comb += h_begin_sav_pos.eq(sink.h_total_line_length - 3)

            # EAV begins right after the end of the active video area
            self.comb += h_begin_eav_pos.eq(sink.h_last_active_pixel + 1)

            self.comb += field.eq(0)  # only support progressive image format

            self.comb += [
                source.h_active.eq(h_active),
                source.v_active.eq(v_active),
                source.field.eq(field),
                source.video_line.eq(v_counter[PIPELINE_FINAL_STEP]),
                source.video_pixel_in_line.eq(h_counter[PIPELINE_FINAL_STEP]),
                source.begin_sav.eq(begin_sav),
                source.begin_eav.eq(begin_eav)
            ]

            self.sync += [
                If(~sink.valid,
                    h_counter[PIPELINE_H_GEN_STEP].eq(SDI_FIRST_PIXEL_NUMBER),
                    v_counter[PIPELINE_V_GEN_STEP].eq(SDI_FIRST_LINE_NUMBER),
                    h_active.eq(0),
                    v_active.eq(0),
                    begin_sav.eq(0),
                    begin_eav.eq(0)

                ).Elif(source.ready,
                    # horizontal timing generation pipeline stage
                    If(h_counter[PIPELINE_H_GEN_STEP] == sink.h_total_line_length,
                        h_counter[PIPELINE_H_GEN_STEP].eq(SDI_FIRST_PIXEL_NUMBER),
                    ).Else(
                        h_counter[PIPELINE_H_GEN_STEP].eq(h_counter[PIPELINE_H_GEN_STEP] + 1)
                    ),

                    # vertical timing generation pipeline stage
                    If(h_counter[PIPELINE_H_GEN_STEP] == h_begin_eav_pos,
                        If(v_counter[PIPELINE_V_GEN_STEP] == sink.v_total_line_number,
                            v_counter[PIPELINE_V_GEN_STEP].eq(SDI_FIRST_LINE_NUMBER)
                        ).Else(
                            v_counter[PIPELINE_V_GEN_STEP].eq(v_counter[PIPELINE_V_GEN_STEP] + 1)
                        )
                    ),

                    # timing generation pipeline stage
                    If(h_counter[PIPELINE_TIMING_STEP] == SDI_FIRST_PIXEL_NUMBER,
                       h_active.eq(1)
                    ).Elif(h_counter[PIPELINE_TIMING_STEP] == sink.h_last_active_pixel,
                        h_active.eq(0)
                    ),

                    begin_sav.eq(h_counter[PIPELINE_TIMING_STEP] == h_begin_sav_pos),
                    begin_eav.eq(h_counter[PIPELINE_TIMING_STEP] == h_begin_eav_pos),

                    If(v_counter[PIPELINE_TIMING_STEP] == sink.v_begin_active_video,
                        v_active.eq(1)
                    ).Elif(v_counter[PIPELINE_TIMING_STEP] == sink.v_end_active_video,
                        v_active.eq(0)
                    )
                )
            ]

            for i in range(len(h_counter) - 1):
                self.sync += h_counter[i].eq(h_counter[i + 1])

            for i in range(len(v_counter) - 1):
                self.sync += v_counter[i].eq(v_counter[i + 1])

        else:
            self.comb += genlock_stream.connect(source)
