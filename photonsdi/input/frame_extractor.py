from migen import *
from photonsdi.constants import *


class FrameExtractor(Module):
    def __init__(self, elementary_stream_count = 2):
        assert elementary_stream_count in [2]
        datapath_width = elementary_stream_count * SDI_ELEMENTARY_STREAM_DATA_WIDTH

        self.i_data = Signal(datapath_width)

        # TODO
