import argparse
import sys
import numpy as np
from tensorflow.keras.models import load_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cipher', type=str, required=True, choices=['PRESENT', 'SIMON', 'SPECK', 'GIFT', 'RECTANGLE'], help='Тип шифра: PRESENT, GIFT, SIMON или SPECK или RECTANGLE')
    parser.add_argument('--block_size', type=int, required=True, help='Размер блока (8,16,32,48,64)')
    parser.add_argument('--rounds', type=int, required=True, help='Число раундов')
    parser.add_argument('--train_samples', type=int, default=100000, help='Примеров для обучения')
    parser.add_argument('--key_size', type=int)
    parser.add_argument('--test_samples', type=int, default=40000, help='Примеров для теста')
    args = parser.parse_args()
    
    if args.cipher == 'PRESENT':
        predict_bits = 80
        if args.key_size is None:
            args.key_size = 80
    elif args.cipher == 'GIFT':
        predict_bits = 128
        if args.key_size is None:
            args.key_size = 128
    else:
        if args.key_size is None:
            raise ValueError("Для SIMON и SPECK и RECTANGLE необходимо указать --key_size")
        predict_bits = args.key_size
    
    try:
        if args.cipher == 'PRESENT':
            data_file = f"data/present_{args.block_size}_80_{args.rounds}_keys.npz"
        elif args.cipher == 'GIFT':
            data_file = f"data/gift_{args.block_size}_128_{args.rounds}_keys.npz"
        else:
            data_file = f"data/{args.cipher.lower()}_{args.block_size}_{args.key_size}_{args.rounds}_keys.npz" 
     
        # Загрузка данных
        data = np.load(data_file, allow_pickle=True)
        keys_bits = data["keys"][args.train_samples:args.train_samples+args.test_samples] #   Тестовая выборка (последние 40k)
        last_round_keys = data["last_round_keys"][args.train_samples:args.train_samples+args.test_samples]

        model_file = f"results/{args.cipher.lower()}_{args.block_size}_{args.rounds}"
        if args.cipher == 'PRESENT':
            model_file += ".weights.h5"
        elif args.cipher == 'GIFT':
            model_file += ".weights.h5"
        else:
            model_file += f"_{args.key_size}.weights.h5"
        
    # Загрузка модели
        model = load_model(model_file)

        # Предсказание
        predictions = model.predict(last_round_keys)
        predicted_bits = np.zeros((len(last_round_keys), predict_bits), dtype=np.uint8)

        for i in range(predict_bits):
            predicted_bits[:, i] = np.argmax(predictions[i], axis=1)

        # Расчет точности
        bit_accuracies = []
        print("\nТочность по битам:")
        for bit in range(predict_bits):
            acc = np.mean(predicted_bits[:, bit] == keys_bits[:, bit])
            bit_accuracies.append(acc)
            print(f"Bit {bit:3d}: {acc:.2%}")

        avg_accuracy = np.mean(bit_accuracies)
        print(f"\nСредняя точность: {avg_accuracy:.2%}")

        result_file = f"results/test_results_{args.cipher}_{predict_bits}bit_{args.rounds}r.txt"
        # Сохранение результатов
        with open(result_file, "w") as f:
            f.write(f"Конфигурация: {args.cipher}_{args.block_size}/{args.key_size}/{args.rounds}r\n")
            f.write(f"Средняя точность: {avg_accuracy * 100:.2f}%\n")
            f.write("Точность по битам:\n")
            for bit in range(predict_bits):
                f.write(f"Bit {bit:3d}: {bit_accuracies[bit]:.2%}\n")
                
    except Exception as e:
        print(f"Ошибка при тестировании: {str(e)}")
        sys.exit(1)
if __name__ == "__main__":
    main()
