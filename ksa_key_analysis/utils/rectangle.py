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
        """Обновление 80-битного ключевого состояния"""
        # 1. Применение S-box к правым 4 колонкам
        for j in range(4):
            nibble = ((key_state[3] >> (4*j))) & 0xF
            nibble |= (((key_state[2] >> (4*j)) & 0xF)) << 4
            nibble |= (((key_state[1] >> (4*j)) & 0xF)) << 8
            nibble |= (((key_state[0] >> (4*j)) & 0xF)) << 12
            s_out = self._apply_sbox(nibble)
            
            key_state[3] = (key_state[3] & ~(0xF << (4*j))) | ((s_out & 0xF) << (4*j))
            key_state[2] = (key_state[2] & ~(0xF << (4*j))) | (((s_out >> 4) & 0xF) << (4*j))
            key_state[1] = (key_state[1] & ~(0xF << (4*j))) | (((s_out >> 8) & 0xF) << (4*j))
            key_state[0] = (key_state[0] & ~(0xF << (4*j))) | (((s_out >> 12) & 0xF) << (4*j))
        
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
        """Обновление 128-битного ключевого состояния"""
        # 1. Применение S-box к правым 8 колонкам
        for j in range(8):
            nibble = ((key_state[3] >> (4*j))) & 0xF
            nibble |= (((key_state[2] >> (4*j)) & 0xF)) << 4
            nibble |= (((key_state[1] >> (4*j)) & 0xF)) << 8
            nibble |= (((key_state[0] >> (4*j)) & 0xF)) << 12
            s_out = self._apply_sbox(nibble)
            
            key_state[3] = (key_state[3] & ~(0xF << (4*j))) | ((s_out & 0xF) << (4*j))
            key_state[2] = (key_state[2] & ~(0xF << (4*j))) | (((s_out >> 4) & 0xF) << (4*j))
            key_state[1] = (key_state[1] & ~(0xF << (4*j))) | (((s_out >> 8) & 0xF) << (4*j))
            key_state[0] = (key_state[0] & ~(0xF << (4*j))) | (((s_out >> 12) & 0xF) << (4*j))
        
        # 2. Feistel-подобное преобразование
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
        
        # 3. Добавление round constant
        rc_mask = (round_const & 0x1F) << 27
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
