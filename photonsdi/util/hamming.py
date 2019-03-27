from operator import xor
from migen import *


# hamming code, also known as (n, k) code

class HammingHelpers(object):
    @staticmethod
    def _calc_symbol(data, generator_matrix, n, k):
        symbol = []
        for i in range(n):
            xor_list = [data[j] for j in range(k) if generator_matrix[i][j] != 0]
            symbol += reduce(xor, xor_list)
        return symbol

    @staticmethod
    def _calc_parity_check_matrix(generator_matrix, n, k):
        # currently only supports non-permutated generator matrix

        # create matrix and fill unity matrix part
        parity_check_matrix = [[1 if i == (j - k) else 0 for j in range(n)] for i in range(n - k)]

        # fill rest of matrix
        for i in range(n - k):
            for j in range(k):
                parity_check_matrix[i][j] = generator_matrix[j][i + k]

        return parity_check_matrix

    @staticmethod
    def _calc_syndrome(data, parity_check_matrix, n, k):
        syndrome = []
        for i in range(n - k):
            xor_list = [data[j] for j in range(n) if parity_check_matrix[i][j] != 0]
            syndrome += reduce(xor, xor_list)
        return syndrome

    def _generate_syndrome_mapping_lut(self, generator_matrix, parity_check_matrix, n, k):
        # currently only supports non-permutated generator matrix

        syndrome_lut = {}   # the case that syndrome is 0 is not covered in this dict
        sample_data = [0 for _ in range(k)]
        sample_symbol = self._calc_symbol(sample_data, generator_matrix, n, k)

        for i in range(k):
            # faulty symbol with exactly one data bit flipped
            faulty_symbol = [sample_symbol[j] ^ 1 if j == i else 0 for j in range(n)]
            syndrome = self._calc_syndrome(faulty_symbol, parity_check_matrix, n, k)
            syndrome_lut[syndrome] = i

        return syndrome_lut


class HammingEncoder(Module, HammingHelpers):
    # assumptions: even parity, non-permutated matrix (left part of generator matrix is unity matrix)

    def __init__(self, generator_matrix):
        assert(len(generator_matrix) > 0)
        n = len(generator_matrix[0])    # total bits (data + parity bits)
        k = len(generator_matrix)       # data bits
        assert(n > k)

        self.i_data = Signal(k)
        self.o_data = Signal(n)

        ###

        self.comb += self.o_data.eq(self._calc_symbol(self.i_data, generator_matrix, n, k))


class HammingDecoder(Module, HammingHelpers):
    # assumptions: even parity, non-permutated matrix (left part of generator matrix is unity matrix)

    def __init__(self, generator_matrix):
        assert(len(generator_matrix) > 0)
        n = len(generator_matrix[0])    # total bits (data + parity bits)
        k = len(generator_matrix)       # data bits
        assert(n > k)

        self.i_data = Signal(n)
        self.o_data = Signal(k)
        self.o_corrected = Signal()

        ###

        parity_check_matrix = self._calc_parity_check_matrix(generator_matrix, n, k)

        syndrome_mapping_lut = self._generate_syndrome_mapping_lut(generator_matrix, parity_check_matrix, n, k)

        syndrome = self._calc_syndrome(self.i_data, parity_check_matrix, n, k)

        if syndrome in syndrome_mapping_lut:
            # one of the data bits is flipped
            bit_flip_pos = syndrome_mapping_lut[syndrome]
        else:
            # none of the data bits is flipped
            bit_flip_pos = None

        for i in range(k):
            self.comb += [
                If(bit_flip_pos is not None and i == bit_flip_pos,
                    self.o_data[i].eq(~self.i_data[i]),
                ).Else(
                    self.o_data[i].eq(self.i_data[i]),
                )
            ]

        self.comb += self.o_corrected.eq(syndrome != 0)
