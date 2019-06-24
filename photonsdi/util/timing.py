from migen import *
from photonsdi.constants import *


# horizontal timing: this is a bit confusing, but it's the SDI standard
# * a line begins right after the last word of the active video data
#   with an EAV packet containing the number of the new line
# * after the blanking area the SAV packet follows which ends right before the
#   wrap-around of the pixel counter
# * at the wrap-around of the pixel counter to 0 the active video line starts

SDI_H_TIMING_PARAMETERS = [
    ("h_total_line_length", SDI_LINE_LENGTH_WIDTH),  # 0-indexed
    ("h_last_active_pixel", SDI_LINE_LENGTH_WIDTH)
]

SDI_V_TIMING_PARAMETERS = [
    ("v_total_line_number", SDI_LINE_NUMBER_WIDTH),  # 1-indexed
    ("v_begin_active_video", SDI_LINE_NUMBER_WIDTH),
    ("v_end_active_video", SDI_LINE_NUMBER_WIDTH)
]  # currently only support for progressive image format, not interlaced or progressive segmented frames

SDI_TIMING_PARAMETERS = SDI_H_TIMING_PARAMETERS + SDI_V_TIMING_PARAMETERS

SDI_XYZ_FLAGS = [
    ("h", 1),
    ("v", 1),
    ("f", 1)
]

SDI_TIMING = [
    ("video_line", SDI_LINE_NUMBER_WIDTH),
    ("video_pixel_in_line", SDI_LINE_LENGTH_WIDTH),  # only valid when h_active is 1
    ("begin_sav", 1),
    ("begin_eav", 1),
    # beware: both h and v active signals have different polarity of h and v signals in xyz word
    ("h_active", 1),  # beware: 0 during both sav/eav words
    ("v_active", 1),
    ("field", 1)
]
