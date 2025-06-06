import argparse
import os
import sys
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import load_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

CIPHER_CONFIG = {
    'PRESENT': {
        'key_bits': 80,
        'model_builder': 'build_ksa_model',
        'require_key_size': False
    },
    'SIMON': {
        'key_bits': lambda args: args.key_size,
        'model_builder': 'build_simon_ksa_model',
        'require_key_size': True
    },
    'SPECK': {
        'key_bits': lambda args: args.key_size,
        'model_builder': 'build_speck_ksa_model',
        'require_key_size': True
    },
    'GIFT': {
        'key_bits': 128,
        'model_builder': 'build_gift_ksa_model',
        'require_key_size': False
    },
    'RECTANGLE': {
        'key_bits': lambda args: args.key_size,
        'model_builder': 'build_rectangle_ksa_model',
        'require_key_size': True
    }
}

def main():
    parser = argparse.ArgumentParser(description='Универсальный скрипт обучения моделей')
    parser.add_argument('--cipher', type=str, required=True,
                      choices=['PRESENT', 'SIMON', 'SPECK', 'GIFT', 'RECTANGLE'],
                      help='Тип шифра')
    parser.add_argument('--block_size', type=int, required=True,
                      help='Размер блока (зависит от шифра)')
    parser.add_argument('--rounds', type=int, required=True,
                      help='Число раундов')
    parser.add_argument('--key_size', type=int,
                      help='Размер ключа (требуется для SIMON/SPECK)')
    parser.add_argument('--epochs', type=int, default=100,
                      help='Число эпох')
    parser.add_argument('--batch_size', type=int, default=200,
                      help='Размер батча')
    parser.add_argument('--train_samples', type=int, default=100000,
                      help='Примеров для обучения')
    parser.add_argument('--test_samples', type=int, default=40000,
                      help='Примеров для теста')
    args = parser.parse_args()
    
    config = CIPHER_CONFIG[args.cipher]
    
    # Проверка параметров
    if config['require_key_size'] and not args.key_size:
        parser.error(f"Для {args.cipher} требуется --key_size")

    # Определение количества бит ключа
    key_bits = config['key_bits'](args) if callable(config['key_bits']) else config['key_bits']

    # Унифицированные имена файлов
    data_file = f"data/{args.cipher.lower()}_{args.block_size}_{key_bits}_{args.rounds}_keys.npz"


    model_file = f"results/{args.cipher.lower()}_{args.block_size}_{args.rounds}"
    if args.cipher in ['SIMON', 'SPECK', 'RECTANGLE']:
        model_file += f"_{args.key_size}.weights.h5"
    else:
            model_file += ".weights.h5"

    try:
        # Загрузка данных
        data = np.load(data_file, allow_pickle=True)
        keys_bits = data["keys"]
        last_round_keys = data["last_round_keys"]

        # Разделение данных
        X_train = last_round_keys[:args.train_samples]
        X_test = last_round_keys[args.train_samples:args.train_samples+args.test_samples]
        y_train = keys_bits[:args.train_samples]
        y_test = keys_bits[args.train_samples:args.train_samples+args.test_samples]

        # One-hot кодирование
        y_train_onehot = [to_categorical(y_train[:, i], num_classes=2) for i in range(key_bits)]
        y_test_onehot = [to_categorical(y_test[:, i], num_classes=2) for i in range(key_bits)]

        # Динамический импорт и построение модели
        module = __import__(f'models.ksa_model', fromlist=[config['model_builder']])
        model_builder = getattr(module, config['model_builder'])
        
        if args.cipher in ['SIMON', 'SPECK', 'RECTANGLE']:
            model = model_builder(args.block_size, args.key_size)
        else:
            model = model_builder(args.block_size)

        # Обучение модели
        model.fit(
            X_train,
            y_train_onehot,
            validation_data=(X_test, y_test_onehot),
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=[EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)],
            verbose=2
        )

        # Сохранение модели
        os.makedirs("results", exist_ok=True)
        model.save(model_file)
        print(f"Модель сохранена в {model_file}")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
