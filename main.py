from LSBR_BMP import LSBR_BMP
from LSBM_BMP import LSBM_BMP
from HammingStego import HammingStego
# from test import LSBR_BMP
# from test2 import LSBM_BMP
# from test3 import HammingStego
import tkinter as tk
from tkinter import filedialog

def main():
    try:
        root = tk.Tk()
        root.withdraw() # Скрыть основное окно

        # Открываем диалог выбора файла
        input_file = filedialog.askopenfilename(
            title="Выберите контейнер для сокрытия",
            filetypes=(("Все файлы", "*.*"), ("Текстовые файлы", "*.txt"))
        )

        # print(input_file.split('/')[-1].split('.')[0])

        if not input_file:
            print("Файл не выбран")
            return
        
        print("Выбранный файл: ", input_file)
        
        # Получаем имя контейнера без расширения
        container_name = input_file.split('/')[-1].split('.')[0]
        # Внедрение сообщения LSB-R
        rate = float(input("Укажите rate внедрения для LSB-R и LSB-M: "))
        # input_file = "life.bmp"
        output_file = f"{container_name}_lsbr_{rate}.bmp"
        secret_message = input('Введите скрываемый текст: ')
        # secret_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magn"
        lsb = LSBR_BMP(input_file)
        lsb.embed(secret_message, output_file, rate)
        print("\nСкрываемое методом LSB-R сообщение внедрено в изображение: ", output_file)
        
        # Извлечение сообщения
        lsbr_stego = LSBR_BMP(output_file)
        lsbr_extracted_message = lsbr_stego.extract(rate).decode('utf-8')
        print("Извлеченное сообщение для метода LSB-R: ", lsbr_extracted_message, '\n')

        # Внедрение сообщения LSB-M
        output_file = f"{container_name}_lsbm_{rate}.bmp"
        lsbm = LSBM_BMP(input_file)
        lsbm.embed(secret_message, output_file, rate)
        print("Скрываемое методом LSB-M сообщение внедрено в изображение: ", output_file)
        
        # Извлечение сообщения
        lsbm_stego = LSBM_BMP(output_file)
        lsbm_extracted_message = lsbm_stego.extract(rate).decode('utf-8')
        print("Извлеченное сообщение для метода LSB-M: ", lsbm_extracted_message, "\n")

        # Внедрение сообщения Хэммингом
        output_file = f"{container_name}_hamming.bmp"
        hamming = HammingStego(input_file)
        hamming.embed(secret_message, output_file)
        print("Скрываемое кодом Хэмминга сообщение внедрено в изображение: ", output_file)
        
        # Извлечение сообщения
        hamming_stego = HammingStego(output_file)
        hamming_extracted_message = hamming_stego.extract().decode('utf-8', errors='ignore')
        print("Извлеченное сообщение для кода Хэмминга: ", hamming_extracted_message)
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()