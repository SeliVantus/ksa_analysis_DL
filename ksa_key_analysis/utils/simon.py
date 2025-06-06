import numpy as np
class SimonCipher:
    z0 = 0b01100111000011010100100010111110110011100001101010010001011111
    z1 = 0b01011010000110010011111011100010101101000011001001111101110001
    z2 = 0b11001101101001111110001000010100011001001011000000111011110101
    z3 = 0b11110000101100111001010001001000000111101001100011010111011011
    z4 = 0b11110111001001010011000011101000000100011011010110011110001011

    def __init__(self, block_size, key_size, rounds=None):
        """
        :block_size: ( 32, 48, 64, 96, 128).
        :key_size: (64, 72, 96, 128, 192, 256).
        """
        self.block_size = block_size  # 32, 48, 64, 96, 128
        self.key_size = key_size     # 64, 72, 96, 128, 192, 256
        self.word_size = block_size // 2  # n
        self.num_words = key_size // self.word_size  # m (2, 3, или 4)
        self.rounds = rounds if rounds is not None else self._get_rounds()
        self.z_sequence = self._get_z_sequence()
        self.mod_mask = (1 << self.word_size) - 1  # Маска для word_size бит
    def _get_rounds(self):
        """Get the number of rounds based on block size and key size."""
        if self.block_size == 32:
            return 32
        elif self.block_size == 48:
            return 36 if self.key_size == 72 else 36
        elif self.block_size == 64:
            return 42 if self.key_size == 96 else 44
        elif self.block_size == 96:
            return 52 if self.key_size == 96 else 54
        elif self.block_size == 128:
            return 68 if self.key_size == 128 else 69 if self.key_size == 192 else 72
        raise ValueError(f"Unsupported block size {self.block_size} or key size {self.key_size}")

    def _get_z_sequence(self):
        """Get the appropriate Z sequence based on block size and key size."""
        if self.block_size == 32:
            return self.z0 if self.key_size == 64 else self.z1
        elif self.block_size == 48:
            return self.z0 if self.key_size == 72 else self.z1
        elif self.block_size == 64:
            return self.z2 if self.key_size == 96 else self.z3
        elif self.block_size == 96:
            return self.z2 if self.key_size == 96 else self.z3
        elif self.block_size == 128:
            return self.z2 if self.key_size == 128 else self.z3 if self.key_size == 192 else self.z4
        raise ValueError(f"Unsupported block size {self.block_size} or key_size {self.key_size}")

    def generate_round_keys(self, master_key, rounds):
        """
        :param master_key: The master key as an integer.
        :return: List of round keys as integers.
        """
        words = []
        for i in range(self.num_words):
            word = (master_key >> (i * self.word_size)) & self.mod_mask
            words.append(word)

        round_keys = words.copy()
        round_constant = self.mod_mask ^ 3  # 0xFFFF...FC

        for i in range(self.num_words, self.rounds):
            # Вычисляем новое слово (аналогично эталонной реализации)
            z_bit = (self.z_sequence >> ((i - self.num_words) % 62)) & 1
            tmp = (words[i - 1] >> 3) | ((words[i - 1] << (self.word_size - 3)) & self.mod_mask)
            if self.num_words == 4:
                tmp ^= words[i - 3]
            tmp ^= (tmp >> 1)
            new_word = (~round_constant & z_bit) ^ tmp ^ words[i - self.num_words]
            round_keys.append(new_word)
            words.append(new_word)

        return round_keys

