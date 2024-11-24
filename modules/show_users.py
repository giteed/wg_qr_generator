#!/usr/bin/env python3
# modules/show_users.py
# Утилита для отображения информации о пользователях WireGuard

import os
import json
from gradio_admin.functions.format_helpers import format_time, calculate_time_remaining
from gradio_admin.wg_users_stats import load_data

# Пути к данным
USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")


def show_all_users():
    """Выводит список всех пользователей с полной информацией."""
    if not os.path.exists(USER_RECORDS_JSON):
        print("❌ Файл user_records.json не найден.")
        return

    try:
        with open(USER_RECORDS_JSON, "r") as file:
            users = json.load(file)
            if not users:
                print("🔍 Пользователи не найдены.")
                return

            print("\n========== Список пользователей ==========")
            for nickname, details in users.items():
                username = nickname
                allowed_ips = details.get("allowed_ips", "N/A")
                recent = details.get("last_handshake", "N/A")
                endpoint = details.get("endpoint", "N/A")
                up = details.get("uploaded", "N/A")
                down = details.get("downloaded", "N/A")
                status = details.get("status", "inactive")
                created = details.get("created", "N/A")
                expires = details.get("expiry", "N/A")

                # Эмодзи для состояния
                recent_emoji = "🟢" if status == "active" else "🔴"
                state_emoji = "✅" if status == "active" else "❌"

                # Форматированный вывод
                print(f"👤 User account : {username}")
                print(f"📧 User e-mail : user@mail.wg")
                print(f"🌱 Created : {format_time(created)}")
                print(f"🔥 Expires : {format_time(expires)}")
                print(f"🌐 intIP {recent_emoji}  : {allowed_ips}")
                print(f"⬆️ up : {up}")
                print(f"🌎 extIP {recent_emoji}  : {endpoint}")
                print(f"⬇️ dw : {down}")
                print(f"📅 TimeLeft : {calculate_time_remaining(expires)}")
                print(f"State : {state_emoji}")
                print("")

            print("==========================================")
    except json.JSONDecodeError:
        print("❌ Ошибка чтения user_records.json.")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
