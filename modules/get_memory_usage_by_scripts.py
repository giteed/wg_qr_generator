#!/usr/bin/env python3

import os
import sys
import time
from prettytable import PrettyTable

# Определяем базовый путь к корню проекта и добавляем его в sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(PROJECT_ROOT)

try:
    from settings import BASE_DIR
except ImportError:
    print("❌ Не удалось найти settings.py. Убедитесь, что файл находится в корневой директории проекта.")
    sys.exit(1)


def get_process_memory_info(project_path):
    """
    Возвращает список процессов, связанных с проектом, и информацию об их потреблении памяти.
    """
    processes = []
    try:
        output = os.popen(f"ps aux --sort=-%mem").readlines()
        for line in output[1:]:  # Пропускаем заголовок
            parts = line.split(maxsplit=10)
            if len(parts) < 11:
                continue
            pid = parts[1]
            memory_percent = float(parts[3])  # Процент использования памяти
            command = parts[10]
            if project_path in command:
                processes.append((pid, memory_percent, command))
    except Exception as e:
        print(f"❌ Ошибка при получении информации о процессах: {e}")
    return processes


def display_memory_usage(interval=5):
    """
    Отображает использование памяти процессами проекта в реальном времени.
    """
    project_path = str(BASE_DIR)
    try:
        while True:
            os.system("clear")
            processes = get_process_memory_info(project_path)

            if not processes:
                print(f"Нет процессов, связанных с проектом: {project_path}")
                time.sleep(interval)
                continue

            # Выводим таблицу
            table = PrettyTable(["PID", "Memory Usage (%)", "Command Line"])
            total_memory_percent = 0.0
            for pid, memory_percent, command in processes:
                table.add_row([pid, f"{memory_percent:.2f}", command])
                total_memory_percent += memory_percent

            print(f"🔍 Процессы, связанные с проектом: {project_path}\n")
            print(table)
            print(f"\nИтоговое использование памяти: {total_memory_percent:.2f}%")
            print(f"Обновление каждые {interval} секунд...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")


if __name__ == "__main__":
    print(f"🔍 Сбор информации о памяти для проекта: {BASE_DIR}")
    display_memory_usage()
