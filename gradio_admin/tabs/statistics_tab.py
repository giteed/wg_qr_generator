#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr
import pandas as pd
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records
from modules.data_sync import sync_user_data  # Для синхронизации данных

def statistics_tab():
    """Возвращает вкладку статистики пользователей WireGuard."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## WireGuard Statistics")

        # Чекбокс для показа неактивных пользователей и кнопка Refresh
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive", value=True)
            refresh_button = gr.Button("Refresh")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Use the search below for filtering.",
                elem_id="user-info-block"  # Для стилизации через CSS
            )

        # Кнопки действий для управления пользователями
        with gr.Row():
            block_button = gr.Button("Block User", elem_id="block-button")
            delete_button = gr.Button("Delete User", elem_id="delete-button")

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)

        # Подсказка для таблицы
        with gr.Row():
            gr.Markdown(
                "Click a cell to view user details after the search.",
                elem_id="table-help-text",
                elem_classes=["small-text"]
            )

        # Таблица с данными пользователей
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's Info", "🆔 Other Info"],
                value=update_table(True),
                interactive=False,  # Таблица только для чтения
                wrap=True
            )

        # Функция для показа информации о выбранном пользователе
        def show_user_info(selected_data, query):
            """Отображает подробную информацию о выбранном пользователе."""
            print("[DEBUG] Вызов функции show_user_info")  # Отладка
            print(f"[DEBUG] Query: {query}")  # Отладка

            if not query.strip():
                return "Please enter a query to filter user data, click a cell, and then perform actions."

            print(f"[DEBUG] Selected data: {selected_data}")  # Отладка
            if selected_data is None or (isinstance(selected_data, pd.DataFrame) and selected_data.empty):
                return "Select a row from the table!"
            try:
                # Если данные предоставлены в виде списка
                if isinstance(selected_data, list):
                    row = selected_data
                # Если данные предоставлены в виде DataFrame
                elif isinstance(selected_data, pd.DataFrame):
                    row = selected_data.iloc[0].values
                else:
                    return "Unsupported data format!"

                print(f"[DEBUG] Extracted row: {row}")  # Отладка

                # Загружаем информацию о пользователе
                username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
                records = load_user_records()
                user_data = records.get(username, {})

                # Форматируем данные для отображения
                user_info = format_user_info(username, user_data, row)
                print(f"[DEBUG] User info:\n{user_info}")  # Отладка
                return user_info.strip()
            except Exception as e:
                print(f"[DEBUG] Error in show_user_info: {e}")  # Отладка
                return f"Error processing data: {str(e)}"

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table, search_input],
            outputs=[selected_user_info]
        )

        # Обновление данных при нажатии кнопки "Refresh"
        def refresh_table(show_inactive):
            """
            Синхронизирует данные, очищает строку поиска, сбрасывает информацию о пользователе и обновляет таблицу.
            """
            sync_user_data()  # Синхронизация данных
            return "", "Please enter a query to filter user data, click a cell, and then perform actions.", update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[search_input, selected_user_info, stats_table]
        )

        # Поиск
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
                table = [
                    row for row in table if query.lower() in " ".join(map(str, row)).lower()
                ]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        # Действия для блокировки и удаления пользователя
        def block_user_action(selected_data):
            """Блокирует выбранного пользователя."""
            if not selected_data:
                return "Please select a user to block."
            # Логика блокировки (добавить)
            return f"User {selected_data[0]} has been blocked."

        def delete_user_action(selected_data):
            """Удаляет выбранного пользователя."""
            if not selected_data:
                return "Please select a user to delete."
            # Логика удаления (добавить)
            return f"User {selected_data[0]} has been deleted."

        block_button.click(
            fn=block_user_action,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )

        delete_button.click(
            fn=delete_user_action,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )
