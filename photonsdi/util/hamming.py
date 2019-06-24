from operator import xor
from migen import *


# hamming code, also known as (n, k) code

class HammingHelpers(object):
    @staticmethod
    def _calc_symbol_xor_bits(data, generator_matrix, n, k):
        symbol_xors = [[] for _ in range(n)]
        for i in range(n):
            symbol_xors[i] = [data[j] for j in range(k) if generator_matrix[j][i] != 0]
        return symbol_xors

    def _calc_symbol(self, data, generator_matrix, n, k):
        symbol = [[] for _ in range(n)]
        symbol_xors = self._calc_symbol_xor_bits(data, generator_matrix, n, k)
        for i in range(n):
            symbol[i] = reduce(xor, list(symbol_xors[i]))
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
    def _calc_syndrome_xor_bits(data, parity_check_matrix, n, k):
        syndrome_xors = [[] for _ in range(n - k)]
        for i in range(n - k):
            syndrome_xors[i] = [data[j] for j in range(n) if parity_check_matrix[i][j] != 0]
        return syndrome_xors

    def _calc_syndrome(self, data, parity_check_matrix, n, k):
        syndrome = [[] for _ in range(n - k)]
        syndrome_xors = self._calc_syndrome_xor_bits(data, parity_check_matrix, n, k)
        for i in range(n - k):
            syndrome[i] = reduce(xor, list(syndrome_xors[i]))
        return syndrome

    def _generate_syndrome_mapping_lut(self, generator_matrix, parity_check_matrix, n, k):
        # currently only supports non-permutated generator matrix
        bitflip_syndrome = [[] for _ in range(k)]   # bit position is index, syndrome is data
        sample_data = [0 for _ in range(k)]
        sample_symbol = self._calc_symbol(sample_data, generator_matrix, n, k)
        for i in range(k):
            # faulty symbol with exactly one data bit flipped
            faulty_symbol = [sample_symbol[j] ^ 1 if j == i else 0 for j in range(n)]
            bitflip_syndrome[i] = self._calc_syndrome(faulty_symbol, parity_check_matrix, n, k)
        return bitflip_syndrome


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

        symbol_bit_xors = self._calc_symbol_xor_bits(self.i_data, generator_matrix, n, k)
        for i in range(n):
            self.comb += self.o_data[i].eq(reduce(xor, symbol_bit_xors[i]))


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

        bitflip_syndrome_lut = self._generate_syndrome_mapping_lut(generator_matrix, parity_check_matrix, n, k)

        data_syndrome_xors = self._calc_syndrome_xor_bits(self.i_data, parity_check_matrix, n, k)
        data_syndrome = Signal(n - k)

        for i in range(n - k):
            self.comb += data_syndrome[i].eq(reduce(xor, list(data_syndrome_xors[i])))

        for i in range(k):
            bitflip_syndrome_i = Signal(n - k)
            for j in range(n - k):
                self.comb += bitflip_syndrome_i[j].eq(bitflip_syndrome_lut[i][j])

            self.comb += [
                If(bitflip_syndrome_i == data_syndrome,
                    self.o_data[i].eq(~self.i_data[i]),
                ).Else(
                    self.o_data[i].eq(self.i_data[i]),
                )
            ]

        self.comb += self.o_corrected.eq(data_syndrome != 0)

