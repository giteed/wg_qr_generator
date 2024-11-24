#!/usr/bin/env python3
# modules/manage_users_menu.py
# Меню для управления пользователями VPN аккаунтов WireGuard

import os
import sys
import subprocess
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users

# Добавляем текущий и родительский каталог в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 👥 Показать всех пользователей")
        print("3. 🗑️ Удалить пользователя")
        print("4. 🔍 Проверить срок действия аккаунта")
        print("5. ➕ Продлить срок действия аккаунта")
        print("6. ♻️ Сбросить срок действия аккаунта")
        print("\n\t0 или q. Вернуться в главное меню")
        print("===============================================")
        choice = input("Выберите действие: ").strip().lower()

        if choice == "1":
            # Создание нового пользователя
            nickname = input("Введите имя пользователя (nickname): ").strip()
            try:
                subprocess.run(["python3", "main.py", nickname])
            except Exception as e:
                print(f"❌ Ошибка при создании пользователя: {e}")

        elif choice == "2":
            # Показать всех пользователей
            show_all_users()

        elif choice == "3":
            # Удаление пользователя
            nickname = input("Введите имя пользователя для удаления: ").strip()
            print(f"🔧 Удаление пользователя {nickname}...")
            # Здесь должна быть реализована функция удаления пользователя

        elif choice == "4":
            # Проверка срока действия
            nickname = input("Введите имя пользователя для проверки: ").strip()
            try:
                result = check_expiry(nickname)
                print(result)
            except ValueError as e:
                print(f"❌ Ошибка: {e}")

        elif choice == "5":
            # Продление срока действия
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            try:
                extend_expiry(nickname, int(days))
                print(f"✅ Срок действия аккаунта {nickname} продлен на {days} дней.")
            except ValueError as e:
                print(f"❌ Ошибка: {e}")

        elif choice == "6":
            # Сброс срока действия
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            try:
                reset_expiry(nickname)
                print(f"✅ Срок действия аккаунта {nickname} сброшен.")
            except ValueError as e:
                print(f"❌ Ошибка: {e}")

        elif choice in ["0", "q"]:
            print("🔙 Возврат в главное меню...")
            break

        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    manage_users_menu()
