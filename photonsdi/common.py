# common constants and defines for the SDI core

SDI_ELEMENTARY_STREAM_DATA_WIDTH = 10
# the 10 bit SDI data words are transmitted LSB first

SDI_CRC_TAPS = [0, 4, 5, 18]
SDI_CRC_LENGTH = max(SDI_CRC_TAPS)
