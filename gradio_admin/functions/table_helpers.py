#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Утилиты для обработки и отображения таблицы в проекте wg_qr_generator

from gradio_admin.functions.format_helpers import format_time, calculate_time_remaining
from gradio_admin.wg_users_stats import load_data

def update_table(show_inactive):
    """Форматирует данные таблицы с дополнительными полями."""
    table = load_data(show_inactive)
    formatted_rows = []

    for row in table:
        username = row[0] if len(row) > 0 else "N/A"
        allowed_ips = row[2] if len(row) > 2 else "N/A"
        recent = row[5] if len(row) > 5 else "N/A"
        endpoint = row[1] if len(row) > 1 else "N/A"
        up = row[4] if len(row) > 4 else "N/A"
        down = row[3] if len(row) > 3 else "N/A"
        status = row[6] if len(row) > 6 else "N/A"
        peer = row[7] if len(row) > 7 else "N/A"  # Добавлено поле peer
        telegram_id = row[8] if len(row) > 8 else "N/A"  # Добавлено поле telegram_id
        created = row[9] if len(row) > 9 else "N/A"
        expires = row[10] if len(row) > 10 else "N/A"

        # Эмодзи для состояния
        recent_emoji = "🟢" if status == "active" else "🔴"
        state_emoji = "✅" if status == "active" else "❌"

        # Формирование строк для пользователя
        formatted_rows.append([f"👤 User account : {username}", f"🆔 Peer : {peer}"])
        formatted_rows.append([f"📧 Telegram ID : {telegram_id}", f"📧 User e-mail : user@mail.wg"])
        formatted_rows.append([f"🌱 Created : {format_time(created)}", f"🔥 Expires : {format_time(expires)}"])
        formatted_rows.append([f"🌐 intIP {recent_emoji}  : {allowed_ips}", f"⬆️ up : {up}"])
        formatted_rows.append([f"🌎 extIP {recent_emoji}  : {endpoint}", f"⬇️ dw : {down}"])
        formatted_rows.append([f"📅 TimeLeft : {calculate_time_remaining(expires)}", f"State : {state_emoji}"])

        # Добавление пустой строки между пользователями
        formatted_rows.append(["", ""])

    return formatted_rows
