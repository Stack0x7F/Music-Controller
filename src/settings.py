import os
import sys

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:

    base_dir = os.path.dirname(os.path.abspath(__file__))


file_path = os.path.join(base_dir, 'settings.txt')

bind = []
try:
    with open(file_path, 'r', encoding='utf-8') as settings:

        keys = settings.readline().strip() 
        for key in keys:
            bind.append(str(key))
            if len(bind) >= 3:
                break
except FileNotFoundError:
    print(f"Ошибка: Файл не найден по пути {file_path}")

print(f"Полученные бинды: {bind}")
