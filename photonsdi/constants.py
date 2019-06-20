# common constants and defines for the SDI core

SDI_ELEMENTARY_STREAM_DATA_WIDTH = 10
# the 10 bit SDI data words are transmitted LSB first

SDI_LINE_LENGTH_WIDTH = 12  # 1080p resolution at maximum for now
SDI_LINE_NUMBER_WIDTH = 11

SDI_FIRST_PIXEL_NUMBER = 0  # pixel 0 is in the middle of a line(!)
SDI_FIRST_LINE_NUMBER = 1

SDI_BLANKING_YRGB_10BIT = 0x040
SDI_BLANKING_CrCb_10BIT = 0x200

SDI_CRC_TAPS = [0, 4, 5, 18]
SDI_CRC_LENGTH = max(SDI_CRC_TAPS)

SDI_SCRAMBLER_TAPS = [0, 4, 9]
SDI_SCRAMBLER_LENGTH = max(SDI_SCRAMBLER_TAPS)

SDI_NRZI_TAPS = [0, 1]
SDI_NRZI_LENGTH = max(SDI_NRZI_TAPS)
