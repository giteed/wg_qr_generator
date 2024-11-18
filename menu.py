#!/usr/bin/env python3
# menu.py
## Меню для управления проектом wg_qr_generator
# Этот скрипт предоставляет интерфейс для запуска тестов, основного скрипта и управления WireGuard.

import os
import subprocess

WIREGUARD_BINARY = "/usr/bin/wg"
WIREGUARD_INSTALL_SCRIPT = "wireguard-install.sh"
CONFIG_DIR = "user/data"
TEST_USER = "test_user"

def check_wireguard_installed():
    """Проверка, установлен ли WireGuard."""
    return os.path.isfile(WIREGUARD_BINARY)

def install_wireguard():
    """Установка WireGuard."""
    if os.path.isfile(WIREGUARD_INSTALL_SCRIPT):
        print("🔧 Установка WireGuard...")
        subprocess.run(["bash", WIREGUARD_INSTALL_SCRIPT])
    else:
        print(f"❌ Скрипт {WIREGUARD_INSTALL_SCRIPT} не найден. Положите его в текущую директорию.")

def remove_wireguard():
    """Удаление WireGuard."""
    print("❌ Удаление WireGuard...")
    subprocess.run(["yum", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL) or \
    subprocess.run(["apt", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL)

def ensure_test_config_exists():
    """Создание тестовой конфигурации, если она отсутствует."""
    config_path = os.path.join(CONFIG_DIR, f"{TEST_USER}.conf")
    if not os.path.exists(config_path):
        print("⚙️  Тестовая конфигурация отсутствует. Создаём тестового пользователя...")
        subprocess.run(["python3", "main.py", TEST_USER])
        print(f"✅ Тестовый пользователь '{TEST_USER}' успешно создан.")
    else:
        print(f"✅ Тестовая конфигурация '{TEST_USER}' уже существует.")

def show_menu():
    """Отображение меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("================== Меню ==================")
        print("1. Запустить тесты")
        print("2. Запустить основной скрипт (main.py)")
        if wireguard_installed:
            print("3. Переустановить WireGuard ♻️")
            print("4. Удалить WireGuard 🗑️")
        else:
            print("3. Установить WireGuard ⚙️")
        print("0. Выход")
        print("==========================================")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            # Проверяем наличие тестовой конфигурации перед тестами
            ensure_test_config_exists()
            print("🔍 Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "2":
            nickname = input("Введите имя пользователя (nickname): ").strip()
            subprocess.run(["python3", "main.py", nickname])
        elif choice == "3":
            install_wireguard()
        elif choice == "4":
            if wireguard_installed:
                remove_wireguard()
            else:
                print("⚠️ WireGuard не установлен.")
        elif choice == "0":
            print("👋 Выход. До свидания!")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    show_menu()
