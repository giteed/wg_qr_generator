#!/usr/bin/env python3
# modules/manage_expiry_menu.py
# Меню для управления сроками действия пользователей

import os
import subprocess
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users  # Импортируем функцию

def manage_expiry_menu():
    """Меню управления сроками действия."""
    while True:
        print("\n========== Управление сроками действия ==========")
        print("1. Показать всех пользователей")
        print("2. Проверить, истек ли срок действия аккаунтов")
        print("3. Продлить срок действия аккаунта")
        print("4. Сбросить срок действия аккаунта")
        print("0. Вернуться в главное меню")
        print("=================================================")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_all_users()  # Вызываем функцию из модуля
        elif choice == "2":
            nickname = input("Введите имя пользователя для проверки: ").strip()
            result = check_expiry(nickname)
            if result["status"] == "expired":
                print(f"Срок действия аккаунта пользователя {nickname} истек.")
            else:
                print(f"Аккаунт пользователя {nickname} еще действителен. {result['remaining_time']}")
        elif choice == "3":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = int(input("Введите количество дней для продления: ").strip())
            extend_expiry(nickname, days)
        elif choice == "4":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            reset_expiry(nickname)
        elif choice in ["0", "q"]:
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")
