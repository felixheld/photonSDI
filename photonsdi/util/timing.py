from migen import *
from photonsdi.constants import *


SDI_H_TIMING_PARAMETERS = [
    ("h_total_line_length", SDI_LINE_LENGTH_WIDTH),  # 0-indexed
    ("h_last_active_pixel", SDI_LINE_LENGTH_WIDTH),
    ("h_begin_sav", SDI_LINE_LENGTH_WIDTH),
    ("h_begin_eav", SDI_LINE_LENGTH_WIDTH)
]  # TODO: document this, since it's very non-obvious

SDI_V_TIMING_PARAMETERS = [
    ("v_total_line_number", SDI_LINE_NUMBER_WIDTH),  # 1-indexed
    ("v_begin_active_video", SDI_LINE_NUMBER_WIDTH),
    ("v_end_active_video", SDI_LINE_NUMBER_WIDTH)
]  # currently only support for progressive image format, not interlaced or progressive segmented frames

SDI_TIMING_PARAMETERS = SDI_H_TIMING_PARAMETERS + SDI_V_TIMING_PARAMETERS

SDI_TIMING_FLAGS = [
    ("h_active", 1),  # beware: 0 during both sav/eav words
    ("v_active", 1),  # beware: both h and v active signals have different polarity of h and v signals in xyz word
    ("field", 1)
]

SDI_TIMING = [
    ("video_line", SDI_LINE_NUMBER_WIDTH),
    ("video_pixel_in_line", SDI_LINE_LENGTH_WIDTH),  # only valid when h_active is 1
    ("begin_sav", 1),
    ("begin_eav", 1)
] + SDI_TIMING_FLAGS
