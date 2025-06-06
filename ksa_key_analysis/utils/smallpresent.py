import numpy as np

class SmallPresent:
    def __init__(self, block_size):
        self.block_size = block_size
        self.sbox = self._generate_sbox()
    
    def _generate_sbox(self):
        # Фиксированный 4-битный S-box для всех размеров блоков
        return [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
                   
    def generate_round_keys(self, master_key, rounds):
        """Генерация раундовых ключей для SmallPresent"""
        key = master_key
        round_keys = []
        
        for i in range(1, rounds+1):
            # Берем младшие block_size бит в качестве раундового ключа
            round_key = key & ((1 << self.block_size) - 1)
            round_keys.append(round_key)
           
            key = ((key & 0x7FFFF) << 61) | (key >> 19)
            
            """Модуль модификации АРК относительно количества S-box"""
            sbox_high = self.sbox[(key >> 76) & 0xF]  # S-box №1 for bits 76-79
            #sbox_mid1  = self.sbox[(key >> 15) & 0xF] # S-box №2 for bits 15-18
            #sbox_low = self.sbox[key & 0xF] #S-box №3 for bits 20-23
            #sbox_mid2 = self.sbox[(key>>20) & 0xF] # S-box №4 for bits 61-64
            #sbox_mid3 = self.sbox[(key>>61) & 0xF] # S-box №5 for bits 76-79
            
            key = (sbox_high << 76) | (key & 0x0FFFFFFFFFFFFFFFFFFF) # having 1 (№1) S-box
            #key = (sbox_high << 76) | (key & 0x0FFFFFFFFFFFFFFFFFF0) | sbox_low # having 2 (№1,2) S-box
            #key = (sbox_high << 76) | (sbox_mid << 15) | sbox_low | (key & 0x0FFFFFFFFFFFFFF87FF0) # having 3 (№1,2,3) S-box
            #key = (sbox_high << 76) | (sbox_mid2 << 20) | (sbox_mid1 << 15) | sbox_low | (key & 0x0FFFFFFFFFFFFF087FF0) # having 4 (№1,2,3,4) S-box
            #key = (sbox_high << 76) | (sbox_mid3 << 61)| (sbox_mid2 << 20) | (sbox_mid1 << 15) | sbox_low | (key & 0x0FFE1FFFFFFFFF087FF0) # having 5 (№1,2,3,4) S-box
            key ^= i << 15
        return round_keys
    
 
