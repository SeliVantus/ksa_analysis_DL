import argparse
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from utils.smallpresent import SmallPresent

def generate_ksa_data(num_samples, block_size, rounds):
    """Генерация датасета для SmallPresent"""
    cipher = SmallPresent(block_size)
    
    # Генерация случайных ключей
    key_bits = np.random.randint(0, 2, size=(num_samples, 80), dtype=np.uint8)
    last_round_keys = np.zeros((num_samples, block_size), dtype=np.uint8)
    
    for i in range(num_samples):
        master_key = int(''.join(map(str, key_bits[i])), 2)
        round_keys = cipher.generate_round_keys(master_key, rounds)
        last_key = round_keys[-1]
        
        # Преобразуем последний ключ в биты
        last_round_keys[i] = np.array([(last_key >> j) & 1 for j in range(block_size)], dtype=np.uint8)
        
    os.makedirs("data", exist_ok=True)   
    np.savez_compressed(f"data/present_{block_size}_80_{rounds}_keys.npz", 
                       keys=key_bits, 
                       last_round_keys=last_round_keys)
    print(f"Сгенерировано {len(key_bits)} примеров для {block_size}-битного блока и {rounds} раундов.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rounds', type=int, required=True)
    parser.add_argument('--block_size', type=int, required=True)
    parser.add_argument('--num_samples', type=int, required=True)
    args = parser.parse_args()
    
    generate_ksa_data(args.num_samples, args.block_size, args.rounds)   

