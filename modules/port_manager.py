# #!/usr/bin/env python3
# modules/port_manager.py
# Скрипт на Python проверяет, занят ли указанный порт, и предлагает пользователю действия: 
# убить процесс, использующий порт, повторно проверить порт или вернуться в меню. 
# Использует библиотеку `psutil` для получения информации о сетевых соединениях и процессах. 
# Обрабатывает ошибки и выводит соответствующие сообщения.

import psutil
import os
import time  # Импортируем модуль time

def handle_port_conflict(port):
    """
    Проверяет, занят ли порт, и предлагает действия пользователю.
    
    :param port: Номер порта для проверки
    :return: Строка действия ("kill", "restart", "exit")
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                pid = conn.pid
                print(" ")
                print(f"\033[1m ==========================================\n ⚠️  Порт {port} уже занят \n ⚠️  процессом с PID 🆔 {pid}.\n ========================================== \033[0m")

                if pid:
                    process_name = psutil.Process(pid).name()
                    print("")
                    print(f" Процесс, использующий порт: {process_name}\n 🔪 (PID {pid}).")
                else:
                    print(f" Не удалось определить процесс, использующий {port} порт.")

                print("\n Доступные действия:\n ==========================================\n")
                print(f" 🔪 1. Убить процесс (PID {pid})")
                print(f" 🔄 2. Проверить порт {port} снова")
                print(" 🔙 3. Вернуться в главное меню")
                print("")
                choice = input(" Выберите действие [1/2/3]: ").strip()
                
                if choice == "1" and pid:
                    try:
                        os.kill(pid, 9)
                        time.sleep(2)
                        print(f"\n ✅  Процесс {process_name} (PID {pid}) был 🔪 завершен 🩸.")
                        return "kill"  # Убить процесс
                    except Exception as e:
                        print(f" ❌ Ошибка при завершении процесса: {e}")
                elif choice == "2":
                    print(f"\n ==========================================\n 🔄 Пытаюсь снова проверить порт {port}...")
                    return "restart"  # Запустить проверку порта снова
                elif choice == "3":
                    #print(" 🔙 Возврат в главное меню.\n")
                    return "exit"  # Вернуться в главное меню
                else:
                    print("")
                    print(" 🔴  Некорректный выбор. \n Возврат в меню.")
                    return "exit"  # Вернуться в главное меню по умолчанию
        # print(f" ✅ Порт {port} свободен. (port_manager.py)\n ==========================================\n ")
        return "ok"
    except Exception as e:
        print(f" ❌ Ошибка: {e}")
        return "exit"  # Вернуться в главное меню в случае ошибки
