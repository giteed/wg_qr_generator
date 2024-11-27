#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)


def prepare_user_choices(show_inactive=True):
    """Создает список пользователей для Dropdown."""
    user_records = load_user_records()
    user_choices = []
    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        user_choices.append(f"{user['username']} ({user['user_id']})")
    return user_choices


def filter_user_choices(search_query, show_inactive):
    """Фильтрует список пользователей на основе ввода."""
    choices = prepare_user_choices(show_inactive)
    if search_query:
        choices = [choice for choice in choices if search_query.lower() in choice.lower()]
    return {"choices": choices, "value": None}


def get_user_info(selected_user):
    """Возвращает подробную информацию о пользователе."""
    if not selected_user:
        return (
            "Начните вводить имя пользователя или выберите его из списка ниже. "
            "После выбора вы сможете увидеть информацию о пользователе и выполнить действия."
        )
    
    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            return json.dumps(user, indent=4)
    return "Пользователь не найден."


def dummy_action(selected_user):
    """Заглушка для кнопок действий."""
    if not selected_user:
        return "Сначала выберите пользователя."
    return f"Действие выполнено для пользователя: {selected_user}"


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Управление пользователями WireGuard")

        # Верхний блок с фильтром и кнопкой обновления
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh")

        # Поле информации о пользователе
        user_info_box = gr.Textbox(
            label="Информация о пользователе",
            lines=10,
            interactive=False,
            value=(
                "Начните вводить имя пользователя или выберите его из списка ниже. "
                "После выбора вы сможете увидеть информацию о пользователе и выполнить действия."
            )
        )

        # Блок кнопок действий
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")
            archive_button = gr.Button("Archive")

        # Поле поиска и выпадающее меню
        with gr.Row():
            search_box = gr.Textbox(
                label="Начните вводить тут",
                placeholder="Введите имя пользователя для поиска...",
                interactive=True
            )
            user_dropdown = gr.Dropdown(
                choices=prepare_user_choices(),
                label="Результаты поиска пользователей",
                interactive=True,
                value=None
            )

        # Логика обновления и действий
        def update_user_choices(search_query, show_inactive):
            """Фильтрует список пользователей на основе ввода."""
            return filter_user_choices(search_query, show_inactive)

        refresh_button.click(
            fn=lambda show_inactive: {"choices": prepare_user_choices(show_inactive), "value": None},
            inputs=[show_inactive_checkbox],
            outputs=user_dropdown
        )
        search_box.change(
            fn=update_user_choices,
            inputs=[search_box, show_inactive_checkbox],
            outputs=user_dropdown
        )
        user_dropdown.change(
            fn=get_user_info,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        block_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        delete_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        archive_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
