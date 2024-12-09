#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator

import os
import sys
import subprocess
from modules.firewall_utils import get_external_ip
from settings import DIAGNOSTICS_LOG

# Установить путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импорт модулей
from modules.wireguard_utils import check_wireguard_installed, install_wireguard, remove_wireguard
from modules.firewall_utils import open_firewalld_port, close_firewalld_port
from modules.gradio_utils import run_gradio_admin_interface
from modules.port_manager import handle_port_conflict
from modules.report_utils import generate_project_report, display_test_report, display_test_summary
from modules.update_utils import update_project
from modules.sync import sync_users_with_wireguard
from modules.manage_users_menu import manage_users_menu
from modules.debugger import run_diagnostics


def show_diagnostics_log():
    """Отображает содержимое журнала диагностики."""
    if os.path.exists(DIAGNOSTICS_LOG):
        print("\n=== 🛠️  Журнал диагностики  ===\n")
        with open(DIAGNOSTICS_LOG, "r") as log_file:
            print(log_file.read())
    else:
        print("\n❌  Журнал диагностики отсутствует.\n")


def show_main_menu():
    """Отображение основного меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("\n==================  Меню  ==================\n")
        print(" i. 🛠️   Информация о состоянии проекта")
        print(" t. 🧪  Запустить тесты")
        print(" up. 🔄  Запустить обновление зависимостей")
        print("--------------------------------------------")
        print(" g. 🌐  Открыть Gradio админку")
        print(" u. 👤  Управление пользователями")
        print(" sy. 📡  Синхронизировать пользователей")
        print(f" du. 🧹  Очистить базу пользователей")
        print("--------------------------------------------")
        if wireguard_installed:
            print(" rw. ♻️   Переустановить WireGuard")
            print(" dw. 🗑️   Удалить WireGuard")
        else:
            print(" iw. ⚙️   Установить WireGuard")
        print(f"--------------------------------------------")

        print(f" rg. 📋  Запустить генерацию отчета")
        print(f" sr. 🗂️   Показать краткий отчет")
        print(f" fr. 📄  Показать полный отчет")
        print(f" dg. 🛠️   Запустить диагностику проекта")
        print(f" sd. 📋  Показать журнал диагностики")  # Новый пункт меню
        print(f"\n\t 0 или q. Выход")
        print(f" ==========================================\n")
        
        choice = input(" Выберите действие: ").strip().lower()

        if choice == "i":
            from modules.project_status import show_project_status
            show_project_status()
        elif choice == "t":
            print("🔍  Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "up":
            update_project()
        elif choice == "g":
            port = 7860
            action = handle_port_conflict(port)
            if action == "ok":
                print(f"\n ✅  Запускаем Gradio интерфейс http://{get_external_ip()}:{port}")
                run_gradio_admin_interface(port=port)
            elif action == "kill":
                print(f" ✅  Теперь запускаем Gradio http://{get_external_ip()}:{port}.")
                run_gradio_admin_interface(port=port)
            elif action == "restart":
                print(f" 🚫 Порт {port} все еще занят.")
            elif action == "exit":
                print(f"\n 🔙 Возврат в главное меню.")
        elif choice == "u":
            manage_users_menu()
        elif choice == "rw":
            remove_wireguard()
            install_wireguard()
        elif choice == "iw" and wireguard_installed:
            remove_wireguard()
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()
        elif choice == "rg":
            print("🔍  Генерация полного отчета...")
            generate_project_report()
        elif choice == "sr":
            print("📂  Отображение краткого отчета...")
            display_test_summary()
        elif choice == "fr":
            print("📄  Отображение полного отчета...")
            display_test_report()
        elif choice == "sy":
            sync_users_with_wireguard()
        elif choice == "dg":
            print("🔍  Запуск диагностики проекта...")
            run_diagnostics()
        elif choice == "sd":
            print("📋  Показ журнала диагностики...")
            show_diagnostics_log()
        elif choice in {"0", "q"}:
            print("\n 👋  Выход. До свидания!\n")
            break
        else:
            print("\n ! ⚠️  Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    show_main_menu()
