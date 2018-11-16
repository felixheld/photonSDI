# common constants and defines for the SDI core

SDI_ELEMENTARY_STREAM_DATA_WIDTH = 10
# the 10 bit SDI data words are transmitted LSB first

SDI_CRC_TAPS = [0, 4, 5, 18]
SDI_CRC_LENGTH = max(SDI_CRC_TAPS)

SDI_SCRAMBLER_TAPS = [0, 4, 9]
SDI_SCRAMBLER_LENGTH = max(SDI_SCRAMBLER_TAPS)

SDI_NRZI_TAPS = [0, 1]
SDI_NRZI_LENGTH = max(SDI_NRZI_TAPS)
