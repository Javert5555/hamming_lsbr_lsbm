import struct
import math
import numpy as np

class HammingStego:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header_size = 54  # Размер заголовка BMP для 24-битных изображений
        
        # Проверочная матрица H для (15,11)-кода Хемминга
        self.H = np.array([
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
        ])
        
        # Чтение файла
        with open(input_file, 'rb') as f:
            self.data = bytearray(f.read())
        
        # Проверка формата файла
        if self.data[0] != ord('B') or self.data[1] != ord('M'):
            raise ValueError("Файл не является BMP-форматом")
        
        self.image_size = len(self.data) - self.header_size
    
    def embed(self, message, output_file):
        """
        Внедрение сообщения с использованием (15,11)-кода Хемминга
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Добавляем длину сообщения (4 байта)
        message_length = len(message)
        message = struct.pack('>I', message_length) + message
        
        # Преобразуем сообщение в биты
        bits = []
        for byte in message:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        
        # Группируем биты по 4 (так как мы кодируем 4 бита в 15 пикселей)
        bit_groups = [bits[i:i+4] for i in range(0, len(bits), 4)]
        
        # Проверяем, достаточно ли места в изображении
        total_pixels_needed = len(bit_groups) * 15
        available_pixels = self.image_size
        
        if total_pixels_needed > available_pixels:
            raise ValueError(f"Сообщение слишком большое для изображения. Нужно {total_pixels_needed} пикселей, доступно {available_pixels}")
        
        # Индекс текущей позиции в данных изображения
        data_index = self.header_size
        
        for group in bit_groups:
            if len(group) < 4:
                # Дополняем последнюю группу нулями, если нужно
                group += [0] * (4 - len(group))
            
            # Получаем младшие биты следующих 15 пикселей
            C = []
            for i in range(15):
                if data_index + i < len(self.data):
                    C.append(self.data[data_index + i] & 1)
                else:
                    C.append(0)  # Если вышли за пределы - добавляем 0
            
            # Вычисляем синдром
            m_vec = np.array(group, dtype=np.uint8).reshape(4, 1)
            C_vec = np.array(C, dtype=np.uint8).reshape(15, 1)
            # print((self.H @ C_vec))
            s = (self.H @ C_vec) % 2
            # print(s)
            # print(m_vec)
            s = s ^ m_vec  # XOR между синдромом и сообщением
            # print(s)
            
            # Вычисляем позицию для изменения (преобразуем биты в число)
            i = int(s[3] * 8 + s[2] * 4 + s[1] * 2 + s[0])

            # Модифицируем i-й бит (если i != 0 и в пределах массива)
            if 0 < i <= 15 and (data_index + i - 1) < len(self.data):
                self.data[data_index + i - 1] ^= 1  # Инвертируем LSB
            
            # Переходим к следующей группе пикселей
            data_index += 15
        
        # Сохранение результата
        with open(output_file, 'wb') as f:
            f.write(self.data)
    
    def extract(self):
        """
        Извлечение сообщения, закодированного с помощью кода Хемминга
        """
        bits = []
        data_index = self.header_size
        
        # Читаем данные, пока не кончится изображение
        while data_index + 15 <= len(self.data):
            # Получаем младшие биты следующих 15 пикселей
            C = []
            for i in range(15):
                C.append(self.data[data_index + i] & 1)
            
            # Вычисляем извлеченное сообщение (4 бита)
            C_vec = np.array(C, dtype=np.uint8).reshape(15, 1)
            m = (self.H @ C_vec) % 2
            
            # Добавляем извлеченные 4 бита
            bits.extend(m.flatten().tolist()[:4])
            
            # Переходим к следующей группе
            data_index += 15
        
        # Преобразуем биты в байты
        # Сначала извлекаем длину сообщения (первые 32 бита)
        message_length = 0
        for i in range(32):
            if i < len(bits):
                message_length = (message_length << 1) | bits[i]
        
        # Затем извлекаем само сообщение
        message_bits = bits[32:32 + message_length*8]
        
        message = bytearray()
        for i in range(0, len(message_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(message_bits):
                    byte = (byte << 1) | message_bits[i + j]
            message.append(byte)
        
        return bytes(message)

# Пример использования
if __name__ == "__main__":
    try:
        # Внедрение сообщения
        input_file = "life.bmp"
        output_file = "life_hamming.bmp"
        # secret_message = "Это никогда не закончится"
        secret_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magn"
        hamming = HammingStego(input_file)
        hamming.embed(secret_message, output_file)
        print(f"Сообщение успешно внедрено в {output_file}")
        
        # Извлечение сообщения
        hamming_stego = HammingStego(output_file)
        extracted_message = hamming_stego.extract().decode('utf-8', errors='ignore')
        print("Извлеченное сообщение:", extracted_message)
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")