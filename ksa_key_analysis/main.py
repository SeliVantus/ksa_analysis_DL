import os
import sys
import subprocess
from argparse import ArgumentParser

def get_cipher_params(cipher_name):
    """Запрашиваем параметры шифра """
    params = {}
    
    if cipher_name == "PRESENT":
        params['rounds'] = int(input("Введите число раундов (1-32): "))
        params['block_size'] = int(input("Введите длину раундового ключа (8,16,32,48,64): "))
        
    elif cipher_name == "SIMON":
        print("Выберите конфигурацию:")
        print("1) 32/64 (default_rounds = 32) \n2) 48/72 (default_rounds = 36) \n3) 48/96 (default_rounds = 36) \n4) 64/96 (default_rounds = 42)")
        print("5) 64/128 (default_rounds = 44) \n6) 96/96 (default_rounds = 52) \n7) 96/144 (default_rounds = 54) \n8) 128/128 (default_rounds = 68) ")
        print("9) 128/192 (default_rounds = 69) \n10) 128/256 (default_rounds = 72) ")
        
        config = input("Ваш выбор (1-10): ")
        configs = {
            '1': {'block_size': 32, 'key_size': 64},
            '2': {'block_size': 48, 'key_size': 72},
            '3': {'block_size': 48, 'key_size': 96},
            '4': {'block_size': 64, 'key_size': 96},
            '5': {'block_size': 64, 'key_size': 128},
            '6': {'block_size': 96, 'key_size': 96},
            '7': {'block_size': 96, 'key_size': 144},
            '8': {'block_size': 128, 'key_size': 128},
            '9': {'block_size': 128, 'key_size': 192},
            '10': {'block_size': 128, 'key_size': 256},
        }
        params.update(configs[config])
        
        params['rounds'] = int(input("Введите число раундов: "))
            
    elif cipher_name == "SPECK":
        print("Выберите конфигурацию:")
        print("1) 32/64 (default_rounds = 22) \n2) 48/72 (default_rounds = 22) \n3) 48/96 (default_rounds = 23) \n4) 64/96 (default_rounds = 26)")
        print("5) 64/128 (default_rounds = 27) \n6) 96/96 (default_rounds = 28) \n7) 96/144 (default_rounds = 29) \n8) 128/128 (default_rounds = 32) ")
        print("9) 128/192 (default_rounds = 33) \n10) 128/256 (default_rounds = 34) ")
        
        config = input("Ваш выбор (1-10): ")
        configs = {
            '1': {'block_size': 32, 'key_size': 64},
            '2': {'block_size': 48, 'key_size': 72},
            '3': {'block_size': 48, 'key_size': 96},
            '4': {'block_size': 64, 'key_size': 96},
            '5': {'block_size': 64, 'key_size': 128},
            '6': {'block_size': 96, 'key_size': 96},
            '7': {'block_size': 96, 'key_size': 144},
            '8': {'block_size': 128, 'key_size': 128},
            '9': {'block_size': 128, 'key_size': 192},
            '10': {'block_size': 128, 'key_size': 256},
        }
        params.update(configs[config])
        params['rounds'] = int(input("Введите число раундов: "))
        
    elif cipher_name == "GIFT":
        print("Выберите версию GIFT:")
        print("1) GIFT-64 (128-битный ключ, 28 раундов по умолчанию)")
        print("2) GIFT-128 (128-битный ключ, 40 раундов по умолчанию)")
    
        config = input("Ваш выбор (1-2): ")
        configs = {
            '1': {'block_size': 64, 'key_size': 128},
            '2': {'block_size': 128, 'key_size': 128}
        }
        params.update(configs[config])
        params['rounds'] = int(input("Введите число раундов: "))
        
    elif cipher_name == "RECTANGLE":
        print("Выберите версию RECTANGLE:")
        print("1) RECTANGLE-80 бит R ( 25 раундов по умолчанию)")
        print("2) RECTANGLE-128 бит K ( 25 раундов по умолчанию)")
    
        config = input("Ваш выбор (1-2): ")
        configs = {
            '1': {'block_size': 64,'key_size': 80},
            '2': {'block_size': 64,'key_size': 128}
        }
        params.update(configs[config])
        params['rounds'] = int(input("Введите число раундов: "))
    

    else:
        print(f"Шифр {cipher_name} пока не поддерживается")
        return None
    
    return params

def get_training_params():
    """Запрашиваем параметры обучения"""
    print("\n=== Параметры обучения ===")
    return {
        'epochs': int(input("Число эпох (рекомендовано 100): ") or 100),
        'batch_size': int(input("Размер пакета (рекомендовано 200): ") or 200),
        'train_samples': int(input("Число пар для обучения (рекомендовано 100000): ") or 100000),
        'test_samples': int(input("Число пар для теста (рекомендовано 40000): ") or 40000)
    }

def main():
    print("=== Анализ алгоритмов развертывания ключа ===")
    
    while True:
        print("\nВыберите шифр:")
        print("1) PRESENT  2) SIMON  3) SPECK")
        print("4) GIFT     5) RECTANGLE  6) Выход")
        
        choice = input("Ваш выбор (1-6): ").strip()
        if choice == '6':
            break
            
        ciphers = {
            '1': 'PRESENT',
            '2': 'SIMON',
            '3': 'SPECK',
            '4': 'GIFT',
            '5': 'RECTANGLE'
        }
        cipher_name = ciphers.get(choice)
        if not cipher_name:
            print("Неверный ввод!")
            continue
            
        # Получаем параметры
        cipher_params = get_cipher_params(cipher_name)
        if not cipher_params:
            continue
            
        train_params = get_training_params()
        
        # Генерация данных
        print("\nГенерация данных...")
        gen_cmd = [
            'python', f'scripts/generate_data_{cipher_name.lower()}.py',
            '--rounds', str(cipher_params['rounds']),
            '--block_size', str(cipher_params.get('block_size', 64)),
            '--num_samples', str(train_params['train_samples'] + train_params['test_samples'])
        ]
        if cipher_name in ['SIMON', 'SPECK', 'RECTANGLE']:
            gen_cmd.extend(['--key_size', str(cipher_params['key_size'])])
        subprocess.run(gen_cmd)
        
        # Обучение модели
        if input("\nНачать обучение? (1 - да, 2 - выход): ") == '1':
            train_cmd = [
                'python', 'scripts/train_model.py',
                '--block_size', str(cipher_params['block_size']),
                '--rounds', str(cipher_params['rounds']),
                '--cipher', cipher_name,
                '--epochs', str(train_params['epochs']),
                '--batch_size', str(train_params['batch_size']),
                '--train_samples', str(train_params['train_samples']),
                '--test_samples', str(train_params['test_samples'])
            ]
            if cipher_name in ['SIMON', 'SPECK', 'RECTANGLE']:
                train_cmd.extend(['--key_size', str(cipher_params['key_size'])])
            try:
                subprocess.run(train_cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при обучении модели: {e}")
                sys.exit(1)
            
            # Тестирование
            if input("\nПротестировать модель? (1 - да, 2 - выход): ") == '1':
                test_cmd = [
                    'python', 'scripts/test_model.py',
                    '--block_size', str(cipher_params['block_size']),
                    '--cipher', cipher_name,
                    '--rounds', str(cipher_params['rounds']),
                    '--test_samples', str(train_params['test_samples']),
                    '--train_samples', str(train_params['train_samples'])
                ]
                if cipher_name in ['SIMON', 'SPECK', 'RECTANGLE']:
                    test_cmd.extend(['--key_size', str(cipher_params['key_size'])])
                subprocess.run(test_cmd)
    
    print("Работа завершена.")

if __name__ == "__main__":
    main()
