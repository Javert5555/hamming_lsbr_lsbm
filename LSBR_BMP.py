import struct
import math

class LSBR_BMP:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header_size = 54  # Размер заголовка BMP (для 24-битных изображений)
        
        # Чтение файла
        with open(input_file, 'rb') as f:
            self.data = bytearray(f.read())
        # print(ord('B'))
        
        # Проверка, что это BMP-файл
        if self.data[0] != ord('B') or self.data[1] != ord('M'):
            raise ValueError("Файл не является BMP-форматом")
        
        # Получаем размер изображения (без заголовка)
        self.image_size = len(self.data) - self.header_size
    
    def embed(self, message, output_file, rate=1.0):
        """
        Внедрение сообщения в изображение методом LSB-R
        
        :param message: строка или байты для внедрения
        :param output_file: имя выходного файла
        :param rate: доля пикселей, используемых для внедрения (0.0-1.0)
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Добавляем длину сообщения в первые 4 байта
        message_length = len(message)
        message = struct.pack('>I', message_length) + message
        print('message_length', message_length * 8)
        # Преобразуем сообщение в биты
        bits = []
        for byte in message:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        
        total_bits = len(bits)
        print('image_size', self.image_size)
        available_bits = math.floor(self.image_size * rate)  # 3 бита на пиксель (RGB)
        
        if total_bits > available_bits:
            raise ValueError("Сообщение слишком большое для изображения с заданным rate")

        print(len(self.data))
        print('total_bits ', total_bits, 'available_bits ', available_bits)

        # Внедряем биты в младшие биты пикселей
        bit_index = 0
        step = math.ceil(1 / rate) if rate < 1.0 else 1 # шаг между пикселями
        
        for i in range(self.header_size, len(self.data)):
            # print(i)
            # if bit_index >= total_bits:
            #     break
            # if (i - self.header_size) % step == 0:
            # print((i - self.header_size) % step)
            if (i - self.header_size) % step == 0 and bit_index < total_bits:
                # Заменяем LSB на бит сообщения
                # print(f"Встраиваемый бит: {bits[bit_index]}")
                # print(f"До встраивания: {self.data[i]:08b}")
                self.data[i] = (self.data[i] & 0xFE) | bits[bit_index]
                # print(f"После встраивания: {self.data[i]:08b}")
                bit_index += 1
            # print(bit_index)
        
        print(bit_index)
        # Сохраняем результат
        with open(output_file, 'wb') as f:
            f.write(self.data)
    
    def extract(self, rate=1.0):
        """
        Извлечение сообщения из изображения
        
        :param rate: доля пикселей, используемых для извлечения (0.0-1.0)
        :return: извлеченное сообщение (в байтах)
        """
        bits = []
        step = math.ceil(1 / rate) if rate < 1.0 else 1
        max_bits = 4 * 8  # 4 байта для длины сообщения (32 бита)
        
        # Сначала извлекаем длину сообщения (первые 32 бита)
        length_bits = []
        length_extracted = False
        message_length = 0
        print('len(self.data)', len(self.data))
        for i in range(self.header_size, len(self.data)):
            if (i - self.header_size) % step == 0:
                # Извлекаем LSB
                bit = self.data[i] & 1
                length_bits.append(bit)
                # print(len(length_bits))
                
                if len(length_bits) == 32 and not length_extracted:
                    # Преобразуем биты в длину сообщения
                    message_length = 0
                    for j in range(32):
                        message_length = (message_length << 1) | length_bits[j]
                    length_extracted = True
                    max_bits = 32 + message_length * 8
                
                if len(bits) >= max_bits:
                    break
        print('max_bits', max_bits)
        print(len(bits))
        # Если не удалось извлечь длину сообщения
        if not length_extracted:
            return b''
        print('len(length_bits)', len(length_bits))
        # Извлекаем само сообщение
        print('message_length', message_length)
        message_bits = length_bits[32:32 + message_length * 8]
        print('32 + message_length * 8', 32 + message_length * 8)
        print(len(message_bits))
        
        # Преобразуем биты в байты
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
    output_file = "life_lsbr_2.bmp"
    secret_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magn"
    print(len(secret_message) * 8)
    lsb = LSBR_BMP(input_file)
    lsb.embed(secret_message, output_file, rate)
    
    # Извлечение сообщения
    lsb_stego = LSBR_BMP(output_file)
    extracted_message = lsb_stego.extract(rate).decode('utf-8')
    print("Извлеченное сообщение:", extracted_message)
    print(len(extracted_message) * 8)
    # print(secret_message == extracted_message)
    # print(len(secret_message))