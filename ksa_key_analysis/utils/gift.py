import numpy as np

class GiftCipher:
    def __init__(self, block_size, rounds=None):
        """
        :param block_size: 64 или 128 (бит)
        :param rounds: число раундов (None для стандартного)
        """
        self.block_size = block_size
        self.rounds = rounds if rounds is not None else (28 if block_size == 64 else 40)
        self.key_size = 128  # Все версии GIFT используют 128-битный ключ

    def _rotate_right(self, val, shift, bits=16):
        """Циклический сдвиг вправо для 16-битного слова"""
        return ((val >> shift) | (val << (bits - shift))) & 0xFFFF

    def generate_round_keys(self, master_key, rounds=None):
        """
        Генерация раундовых ключей для GIFT
        :param master_key: исходный 128-битный ключ (int)
        :param rounds: количество раундов (если None - используется self.rounds)
        :return: список раундовых ключей (int)
        """
        num_rounds = rounds if rounds is not None else self.rounds
        
        # Инициализация ключевого состояния (8 x 16-битных слов)
        key_state = [
            (master_key >> (i * 16)) & 0xFFFF 
            for i in reversed(range(8))
        ]
        
        round_keys = []
        
        for _ in range(num_rounds):
            # Извлечение раундового ключа
            if self.block_size == 64:
                # GIFT-64: RK = k1 || k0
                rk = (key_state[1] << 16) | key_state[0]
            else:
                # GIFT-128: RK = k5 || k4 || k1 || k0
                rk = (key_state[5] << 48) | (key_state[4] << 32) | (key_state[1] << 16) | key_state[0]
            
            round_keys.append(rk)
            
            # Обновление ключевого состояния
            temp_state = [0] * 8
            
            # Весь ключ сдвигается на 32 бита (2 слова)
            for i in range(8):
                temp_state[i] = key_state[(i + 2) % 8]
            
            # Применение вращений к k0 и k1
            temp_state[0] = self._rotate_right(key_state[0], 12)
            temp_state[1] = self._rotate_right(key_state[1], 2)
            
            # Обновление состояния
            key_state = temp_state
        
        return round_keys
