from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_ksa_model(block_size):
    """Создает модель в зависимости от размера блока"""
    inputs = Input(shape=(block_size,), name="input_layer")
    
    # Архитектура зависит от размера блока
    if block_size == 8:
        # Вход: 8 нейронов
        x = Dense(4, activation='relu')(inputs)  # Скрытый слой 1: 4 нейрона
        x = Dense(2, activation='relu')(x)       # Скрытый слой 2: 2 нейрона       
    elif block_size == 16:
        # Вход: 16 нейронов
        x = Dense(8, activation='relu')(inputs)  # Скрытый слой 1: 8 нейронов
        x = Dense(4, activation='relu')(x)       # Скрытый слой 2: 4 нейрона     
    elif block_size == 32:
        # Вход: 32 нейрона
        x = Dense(24, activation='relu')(inputs)  # Скрытый слой 1: 24 нейрона
        x = Dense(12, activation='relu')(x)      # Скрытый слой 2: 12 нейронов
        x = Dense(8, activation='relu')(x)       # Скрытый слой 3: 8 нейронов   
    elif block_size == 48:
        # Вход: 48 нейронов
        x = Dense(24, activation='relu')(inputs)  # Скрытый слой 1: 24 нейрона
        x = Dense(16, activation='relu')(x)      # Скрытый слой 2: 16 нейронов
        x = Dense(8, activation='relu')(x)       # Скрытый слой 3: 8 нейронов  
    elif block_size == 64:
        # Вход: 64 нейрона
        x = Dense(32, activation='relu')(inputs)  # Скрытый слой 1: 32 нейрона
        x = Dense(16, activation='relu')(x)      # Скрытый слой 2: 16 нейронов
        x = Dense(8, activation='relu')(x)       # Скрытый слой 3: 8 нейронов


    else:
        raise ValueError(f"Unsupported block size: {block_size}")
    
    # Выходной слой - предсказание битов ключа
   # key_size = block_size  # Для SmallPresent размер ключа равен размеру блока
    outputs = [Dense(2, activation='softmax', name=f"bit_{i}_output")(x) for i in range(80)]
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'] * 80)
    return model
    
def build_simon_ksa_model(block_size, key_size):
    n = block_size // 2  # Размер раундового ключа = n
    inputs = Input(shape=(n,), name="input_layer")
    
    # Общая архитектура скрытых слоев
    if n == 16:  # SIMON32/64
        x = Dense(8, activation='relu')(inputs)
        x = Dense(4, activation='relu')(x)
    elif n == 24:  # SIMON48/72, SIMON48/96
        x = Dense(16, activation='relu')(inputs)
        x = Dense(8, activation='relu')(x)
    elif n == 32:  # SIMON64/96, SIMON64/128
        x = Dense(24, activation='relu')(inputs)
        x = Dense(12, activation='relu')(x)
        x = Dense(8, activation='relu')(x)
    elif n == 48:  # SIMON96/96, SIMON96/144
        x = Dense(24, activation='relu')(inputs)
        x = Dense(16, activation='relu')(x)
        x = Dense(8, activation='relu')(x)
    elif n == 64:  # SIMON128/128, SIMON128/192, SIMON128/256
        x = Dense(32, activation='relu')(inputs)
        x = Dense(16, activation='relu')(x)
        x = Dense(8, activation='relu')(x)
    else:
        raise ValueError(f"Unsupported block size: {block_size}")
    
    # Выходной слой: key_size бинарных классификаторов
    outputs = [Dense(2, activation='softmax', name=f"bit_{i}_output")(x) for i in range(key_size)]
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'] * key_size)
    return model
    
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_speck_ksa_model(block_size, key_size):
    """Создает модель для анализа ключей SPECK."""
    n = block_size // 2  # Размер раундового ключа
    
    inputs = Input(shape=(n,), name="input_layer")
    
    # Универсальная архитектура
    if n <= 16:
        x = Dense(32, activation='relu')(inputs)
        x = Dense(64, activation='relu')(x)
    elif n <= 32:
        x = Dense(64, activation='relu')(inputs)
        x = Dense(128, activation='relu')(x)
    else:
        x = Dense(128, activation='relu')(inputs)
        x = Dense(256, activation='relu')(x)
        x = Dense(128, activation='relu')(x)
    
    outputs = [Dense(2, activation='softmax', name=f"bit_{i}_output")(x) 
              for i in range(key_size)]
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'] * key_size)
    return model
    
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_gift_ksa_model(block_size):
    n = block_size // 2
    inputs = Input(shape=(block_size,))
    
    # Архитектура зависит от размера блока
    if n == 32:
        x = Dense(24, activation='relu')(inputs)
        x = Dense(12, activation='relu')(x)
        x = Dense(8, activation='relu')(x)
    elif n == 64:
        x = Dense(32, activation='relu')(inputs)
        x = Dense(16, activation='relu')(x)
        x = Dense(8, activation='relu')(x)
    else:
        raise ValueError(f"Unsupported block size: {block_size}")
    
    # Выходной слой - предсказание 128 бит ключа
    outputs = [Dense(2, activation='softmax', name=f"bit_{i}_output")(x) for i in range(128)]
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'] * 128)
    return model
    
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_rectangle_ksa_model(block_size, key_size):
    inputs = Input(shape=(block_size,))
    
    # Архитектура зависит от размера блока
    x = Dense(32, activation='relu')(inputs)
    x = Dense(16, activation='relu')(x)
    x = Dense(8, activation='relu')(x)

    # Выходной слой - предсказание 128 бит ключа
    outputs = [Dense(2, activation='softmax', name=f"bit_{i}_output")(x) for i in range(key_size)]
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'] * key_size)
    return model
