import numpy as np

class RectangleCipher:
    # S-box для RECTANGLE
    SBOX = [6, 5, 12, 10, 1, 14, 7, 9, 11, 0, 3, 13, 8, 15, 4, 2]
    
    def __init__(self, block_size, key_size, rounds=None):
        """
        :param key_size: 80 или 128 (бит)
        :param rounds: число раундов (по умолчанию 25)
        """
        if key_size not in [80, 128]:
            raise ValueError("RECTANGLE supports only 80 or 128-bit keys")
        self.key_size = key_size
        self.rounds = rounds if rounds is not None else 25
        self.block_size = block_size
        
    def _apply_sbox(self, word):
        """Применение S-box к 4-битному слову"""
        return self.SBOX[word]
        
    def _key_update_80bit(self, key_state, round_const):
        for j in range(4):
        # Получаем 4 nibble из текущей колонки j
            nibble3 = (key_state[3] >> (4*j)) & 0xF
            nibble2 = (key_state[2] >> (4*j)) & 0xF
            nibble1 = (key_state[1] >> (4*j)) & 0xF
            nibble0 = (key_state[0] >> (4*j)) & 0xF
        
        # Применяем S-box к каждому nibble
            s_out3 = self._apply_sbox(nibble3)
            s_out2 = self._apply_sbox(nibble2)
            s_out1 = self._apply_sbox(nibble1)
            s_out0 = self._apply_sbox(nibble0)
        
        # Обновляем ключевое состояние
            key_state[3] = (key_state[3] & ~(0xF << (4*j))) | (s_out3 << (4*j))
            key_state[2] = (key_state[2] & ~(0xF << (4*j))) | (s_out2 << (4*j))
            key_state[1] = (key_state[1] & ~(0xF << (4*j))) | (s_out1 << (4*j))
            key_state[0] = (key_state[0] & ~(0xF << (4*j))) | (s_out0 << (4*j))
    
    # 2. Feistel-подобное преобразование
        row0 = ((key_state[0] << 8) | (key_state[0] >> 8)) & 0xFFFF
        row0 ^= key_state[1]
        row3 = ((key_state[3] << 12) | (key_state[3] >> 4)) & 0xFFFF
        row3 ^= key_state[4]
    
        new_state = [
            row0,
            key_state[2],
            key_state[3],
            row3,
            key_state[0]
        ]
    
    # 3. Добавление round constant
        rc_mask = (round_const & 0x1F) << 11
        new_state[0] ^= rc_mask
    
        return new_state
    
    def _key_update_128bit(self, key_state, round_const):
        for j in range(8):
            # Получаем 4 nibble из текущей колонки j
            nibble3 = (key_state[3] >> (4*j)) & 0xF
            nibble2 = (key_state[2] >> (4*j)) & 0xF
            nibble1 = (key_state[1] >> (4*j)) & 0xF
            nibble0 = (key_state[0] >> (4*j)) & 0xF
        
        # Применяем S-box к каждому nibble
            s_out3 = self._apply_sbox(nibble3)
            s_out2 = self._apply_sbox(nibble2)
            s_out1 = self._apply_sbox(nibble1)
            s_out0 = self._apply_sbox(nibble0)
        
        # Обновляем ключевое состояние
            key_state[3] = (key_state[3] & ~(0xF << (4*j))) | (s_out3 << (4*j))
            key_state[2] = (key_state[2] & ~(0xF << (4*j))) | (s_out2 << (4*j))
            key_state[1] = (key_state[1] & ~(0xF << (4*j))) | (s_out1 << (4*j))
            key_state[0] = (key_state[0] & ~(0xF << (4*j))) | (s_out0 << (4*j))
    
    # 2. Feistel-подобное преобразование для 128-битного ключа
        row0 = ((key_state[0] << 8) | (key_state[0] >> 24)) & 0xFFFFFFFF
        row0 ^= key_state[1]
        row2 = ((key_state[2] << 16) | (key_state[2] >> 16)) & 0xFFFFFFFF
        row2 ^= key_state[3]
    
        new_state = [
            row0,
            key_state[2],
            row2,
            key_state[0]
        ]
    
    # 3. Добавление round constant (для 128-бит смещение другое)
        rc_mask = (round_const & 0x1F) << 27  # 27-й бит для 128-битного варианта
        new_state[0] ^= rc_mask
    
        return new_state
    
    def _generate_round_constants(self):
        """Генерация round constants (5-битный LFSR)"""
        rc = [0x01]  # Начальное значение
        for _ in range(1, self.rounds):
            new_bit = (rc[-1] >> 4) ^ (rc[-1] >> 2)
            rc.append(((rc[-1] << 1) | (new_bit & 1)) & 0x1F)
        return rc
    
    def generate_round_keys(self, master_key, rounds=None):
        """
        Генерация раундовых ключей
        :param master_key: исходный ключ (int)
        :param rounds: количество раундов (если None - используется self.rounds)
        :return: список 64-битных раундовых ключей
        """
        num_rounds = rounds if rounds is not None else self.rounds
        round_constants = self._generate_round_constants()
        round_keys = []
        
        if self.key_size == 80:
            # Инициализация 80-битного ключевого состояния (5x16 бит)
            key_state = [
                (master_key >> (i*16)) & 0xFFFF for i in range(4, -1, -1)
            ]
            
            for r in range(num_rounds + 1):  # +1 для последнего ключа
                # Извлечение раундового ключа (первые 4 строки)
                round_key = ((key_state[3] & 0xFFFF) << 48) | \
                           ((key_state[2] & 0xFFFF) << 32) | \
                           ((key_state[1] & 0xFFFF) << 16) | \
                           (key_state[0] & 0xFFFF)
                round_keys.append(round_key)
                
                if r < num_rounds:
                    key_state = self._key_update_80bit(key_state, round_constants[r])
        
        else:  # 128 бит
            # Инициализация 128-битного ключевого состояния (4x32 бит)
            key_state = [
                (master_key >> (i*32)) & 0xFFFFFFFF for i in range(3, -1, -1)
            ]
            
            for r in range(num_rounds + 1):
                # Извлечение раундового ключа (16 правых колонок)
                round_key = ((key_state[3] & 0xFFFF) << 48) | \
                           ((key_state[2] & 0xFFFF) << 32) | \
                           ((key_state[1] & 0xFFFF) << 16) | \
                           (key_state[0] & 0xFFFF)
                round_keys.append(round_key)
                
                if r < num_rounds:
                    key_state = self._key_update_128bit(key_state, round_constants[r])
        
        return round_keys
