#!/usr/bin/env python3
# modules/manage_users_menu.py
# Модуль для управления пользователями WireGuard

import os
import json

USER_RECORDS_FILE = "user/data/user_records.json"
DEFAULT_ALLOWED_IPS = "10.66.66.0/24"  # Значение по умолчанию для разрешённых IP


def ensure_directory_exists(filepath):
    """Убедитесь, что директория для файла существует."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_user_records():
    """Загрузка данных пользователей из JSON."""
    if os.path.exists(USER_RECORDS_FILE):
        with open(USER_RECORDS_FILE, "r") as file:
            return json.load(file)
    return {}


def save_user_records(user_records):
    """Сохранение данных пользователей в JSON."""
    ensure_directory_exists(USER_RECORDS_FILE)
    with open(USER_RECORDS_FILE, "w") as file:
        json.dump(user_records, file, indent=4)


def create_user():
    """Создание нового пользователя."""
    username = input("Введите имя пользователя: ").strip()
    if not username:
        print("❌ Имя пользователя не может быть пустым.")
        return

    allowed_ips = input("Введите разрешённые IP (например, 10.66.66.5): ").strip() or DEFAULT_ALLOWED_IPS

    records = load_user_records()
    if username in records:
        print("❌ Пользователь с таким именем уже существует.")
        return

    records[username] = {
        "username": username,
        "allowed_ips": allowed_ips,
        "status": "inactive",
    }
    save_user_records(records)
    print(f"✅ Пользователь {username} успешно создан с разрешёнными IP: {allowed_ips}")


def list_users():
    """Вывод списка всех пользователей."""
    records = load_user_records()
    if not records:
        print("⚠️ Список пользователей пуст.")
        return

    print("\n👤 Пользователи WireGuard:")
    for username, data in records.items():
        allowed_ips = data.get("allowed_ips", "N/A")
        status = data.get("status", "N/A")
        print(f"  - {username}: {allowed_ips} | Статус: {status}")


def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 🔍 Показать всех пользователей")
        print("0. Вернуться в главное меню")
        print("===============================================")

        choice = input("Выберите действие: ").strip()
        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice in {"0", "q"}:
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте снова.")
