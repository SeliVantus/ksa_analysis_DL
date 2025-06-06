import numpy as np
class SpeckCipher:
    """Реализация шифра SPECK с корректным расширением ключа."""
    
    # Конфигурации: (block_size, key_size) → rounds
    _CONFIGS = {
        (32, 64),
        (48, 72), (48, 96),
        (64, 96), (64, 128),
        (96, 96), (96, 144),
        (128, 128), (128, 192), (128, 256)
    }

    def __init__(self, block_size, key_size, rounds=None):
        """
        :param block_size: 32, 48, 64, 96, 128
        :param key_size: зависит от block_size
        """
        if (block_size, key_size) not in self._CONFIGS:
            raise ValueError(f"Unsupported configuration: block_size={block_size}, key_size={key_size}")

        self.block_size = block_size
        self.key_size = key_size
        self.word_size = block_size // 2  # n
        self.m = key_size // self.word_size  # 2, 3 или 4
        self.rounds = rounds if rounds is not None else self._get_rounds()
        self.mod_mask = (1 << self.word_size) - 1
        
        # Параметры сдвигов
        self.alpha = 8 if block_size != 32 else 7
        self.beta = 3 if block_size != 32 else 2
        
    def _get_rounds(self):
        """Get the number of rounds based on block size and key size."""
        if self.block_size == 32:
            return 22
        elif self.block_size == 48:
            return 22 if self.key_size == 72 else 23
        elif self.block_size == 64:
            return 26 if self.key_size == 96 else 27
        elif self.block_size == 96:
            return 28 if self.key_size == 96 else 29
        elif self.block_size == 128:
            return 32 if self.key_size == 128 else 33 if self.key_size == 192 else 34
        raise ValueError(f"Unsupported block size {self.block_size} or key size {self.key_size}")

    def _rotate_right(self, val, shift):
        return ((val >> shift) | (val << (self.word_size - shift))) & self.mod_mask

    def _rotate_left(self, val, shift):
        return ((val << shift) | (val >> (self.word_size - shift))) & self.mod_mask

    def generate_round_keys(self, master_key, rounds):
        """Генерация раундовых ключей по мастер-ключу."""
        # Разбиваем ключ на слова (l[m-2], ..., l[0], k[0])
        words = []
        for i in range(self.m):
            words.append((master_key >> (i * self.word_size)) & self.mod_mask)
        
        k = [words.pop()]  # k[0] - последнее слово
        l = words[::-1]    # l[0..m-2]
        
        for i in range(self.rounds - 1):
            # l[i+m-1] = (k[i] + S^-α(l[i])) ⊕ i
            new_l = ((k[i] + self._rotate_right(l[i], self.alpha)) & self.mod_mask) ^ i
            # k[i+1] = S^β(k[i]) ⊕ l[i+m-1]
            new_k = self._rotate_left(k[i], self.beta) ^ new_l
            
            l.append(new_l)
            k.append(new_k)
        
        return k
