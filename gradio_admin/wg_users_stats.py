#!/usr/bin/env python3
# gradio_admin/wg_users_stats.py
# Скрипт для работы со статистикой пользователей WireGuard в проекте wg_qr_generator


import os
import json

# Путь к файлу JSON
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_LOG_PATH = os.path.join(PROJECT_ROOT, "logs/wg_users.json")


def load_data(show_inactive):
    """
    Загружает данные пользователей WireGuard из JSON-файла и фильтрует их.
    """
    try:
        print(f"Путь к JSON: {JSON_LOG_PATH}")  # Отладка
        with open(JSON_LOG_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON-файл не найден!")
        return [["Нет данных о пользователях"]]
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return [["Ошибка чтения JSON-файла"]]

    users = data.get("users", {})
    print(f"Загруженные пользователи: {users}")  # Отладка

    table = []

    for username, user_data in users.items():
        if not show_inactive and user_data["status"] == "inactive":
            continue
        
        # Стилизация статуса
        status_color = "green" if user_data["status"] == "active" else "red"
        status_html = f"<span style='color: {status_color}'>{user_data['status']}</span>"

        table.append([
            username or "Неизвестно",
            ", ".join(user_data.get("endpoints", ["Нет данных"])),
            user_data.get("allowed_ips", "Нет данных"),
            user_data["total_transfer"]["received"],
            user_data["total_transfer"]["sent"],
            user_data["last_handshake"] or "Никогда",
            status_html  # HTML для статуса
        ])

    print(f"Форматированная таблица перед возвратом: {table}")  # Отладка
    return table
