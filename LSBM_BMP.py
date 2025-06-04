import struct
import math
import random

class LSBM_BMP:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header_size = 54  # Размер заголовка BMP для 24-битных изображений
        
        # Чтение файла
        with open(input_file, 'rb') as f:
            self.data = bytearray(f.read())
        
        # Проверка формата файла
        if self.data[0] != ord('B') or self.data[1] != ord('M'):
            raise ValueError("Файл не является BMP-форматом")
        
        self.image_size = len(self.data) - self.header_size
    
    def embed(self, message, output_file, rate=1.0):
        """
        Внедрение сообщения методом LSB-Matching
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
        
        total_bits = len(bits)
        available_bits = math.floor(self.image_size * rate)
        
        if total_bits > available_bits:
            raise ValueError("Сообщение слишком большое для изображения с заданным rate")
        
        # Внедряем биты с использованием LSB-Matching
        bit_index = 0
        step = math.ceil(1 / rate) if rate < 1.0 else 1
        
        for i in range(self.header_size, len(self.data)):
            if (i - self.header_size) % step == 0 and bit_index < total_bits:
                current_bit = bits[bit_index]
                current_byte = self.data[i]
                current_lsb = current_byte & 1
                
                if current_bit == current_lsb:
                    # Бит уже совпадает - ничего не меняем
                    pass
                else:
                    if current_byte == 0:
                        # Особый случай: можно только увеличить на 1
                        self.data[i] = 1
                    elif current_byte == 255:
                        # Особый случай: можно только уменьшить на 1
                        self.data[i] = 254
                    else:
                        # Случайный выбор между +1 и -1
                        # Если скрываемый бит = 1, а последний бит self.data[i] будет = 0, то при +1 или -1, последний бит self.data[i] всё равно станет = 1
                        # И наоборот, если скрываемый бит = 0, а последний бит self.data[i] будет = 1, то при +1 или -1, последний бит self.data[i] всё равно станет = 0
                        self.data[i] = current_byte + random.choice([-1, 1])
                
                bit_index += 1
        
        # Сохранение результата
        with open(output_file, 'wb') as f:
            f.write(self.data)
    
    def extract(self, rate=1.0):
        """
        Извлечение сообщения (аналогично LSB-R, так как биты все равно в LSB)
        """
        bits = []
        step = math.ceil(1 / rate) if rate < 1.0 else 1
        max_bits = 4 * 8  # Максимум для длины сообщения
        
        length_bits = []
        length_extracted = False
        message_length = 0
        
        for i in range(self.header_size, len(self.data)):
            if (i - self.header_size) % step == 0:
                bit = self.data[i] & 1
                bits.append(bit)
                length_bits.append(bit)
                
                if len(length_bits) == 32 and not length_extracted:
                    message_length = 0
                    for j in range(32):
                        message_length = (message_length << 1) | length_bits[j]
                    length_extracted = True
                    max_bits = 32 + message_length * 8
                
                if len(bits) >= max_bits:
                    break
        
        if not length_extracted:
            return b''
        
        message_bits = bits[32:32 + message_length * 8]
        
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
    # Внедрение сообщения
    rate = .25
    input_file = "life.bmp"
    output_file = "life_lsbm_25.bmp"
    # secret_message = "Это никогда не закончится"
    secret_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magn"
    lsbm = LSBM_BMP(input_file)
    lsbm.embed(secret_message, output_file, rate)
    
    # Извлечение сообщения
    lsbm_stego = LSBM_BMP(output_file)
    extracted_message = lsbm_stego.extract(rate).decode('utf-8')
    print("Извлеченное сообщение:", extracted_message)