import gradio as gr
import os
import json
import subprocess
from datetime import datetime

# Utility functions
def create_user(username):
    """Создание нового пользователя."""
    if not username:
        return "Ошибка: имя пользователя не может быть пустым."
    try:
        subprocess.run(["python3", "main.py", username], check=True)
        return f"✅ Пользователь {username} успешно создан."
    except Exception as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}"

def list_users():
    """Чтение списка пользователей из user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    try:
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        if not user_data:
            return "❌ Нет зарегистрированных пользователей."

        users_list = []
        for username, details in user_data.items():
            user_info = (
                f"👤 Пользователь: {username}\n"
                f"   📅 Создан: {details.get('created_at', 'N/A')}\n"
                f"   ⏳ Истекает: {details.get('expires_at', 'N/A')}\n"
                f"   🌐 Адрес: {details.get('address', 'N/A')}"
            )
            users_list.append(user_info)

        return "\n\n".join(users_list)

    except json.JSONDecodeError:
        return "❌ Ошибка чтения файла user_records.json. Проверьте его формат."

def delete_user(username):
    """Ручное удаление пользователя, с учётом всех операций."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    stale_records_path = os.path.join("user", "stale_user_records.json")
    user_file = os.path.join("user", "data", f"{username}.conf")
    stale_config_dir = os.path.join("user", "stale_config")
    ip_records_path = os.path.join("user", "data", "ip_records.json")
    wg_config_path = os.path.join("user", "data", "wg_configs")

    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    if not os.path.exists(user_file):
        return f"❌ Пользователь {username} не найден."

    # Создаём папку для устаревших конфигураций, если её нет
    os.makedirs(stale_config_dir, exist_ok=True)

    try:
        # Читаем записи о пользователях
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        # Читаем IP-адреса
        with open(ip_records_path, "r") as f:
            ip_data = json.load(f)

        # Читаем записи об устаревших пользователях
        if os.path.exists(stale_records_path):
            with open(stale_records_path, "r") as f:
                stale_data = json.load(f)
        else:
            stale_data = {}

        if username not in user_data:
            return f"❌ Пользователь {username} не найден в user_records.json."

        # Переносим данные в архив
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        stale_data[username] = user_info

        # Освобождаем IP-адрес
        ip_address = user_info.get("address", "").split("/")[0]
        if ip_address in ip_data:
            ip_data[ip_address] = False

        # Перемещаем файл конфигурации
        stale_config_path = os.path.join(stale_config_dir, f"{username}.conf")
        os.rename(user_file, stale_config_path)

        # Удаляем пользователя из WireGuard
        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                wg_config = f.read()
            updated_config = "\n".join(
                line
                for line in wg_config.splitlines()
                if username not in line
            )
            with open(wg_config_path, "w") as f:
                f.write(updated_config)
            # Применяем изменения
            subprocess.run(["wg", "syncconf", "wg0", wg_config_path])

        # Сохраняем обновлённые данные
        with open(user_records_path, "w") as f:
            json.dump(user_data, f, indent=4)

        with open(stale_records_path, "w") as f:
            json.dump(stale_data, f, indent=4)

        with open(ip_records_path, "w") as f:
            json.dump(ip_data, f, indent=4)

        return f"✅ Пользователь {username} успешно удалён и перемещён в архив."

    except Exception as e:
        return f"❌ Ошибка при удалении пользователя: {str(e)}"

# Gradio interface
with gr.Blocks() as admin_interface:
    gr.Markdown("## Админка для управления WireGuard")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Создать пользователя")
            username_input = gr.Textbox(label="Имя пользователя")
            create_button = gr.Button("Создать")
            create_output = gr.Textbox(label="Результат создания")
            create_button.click(create_user, inputs=username_input, outputs=create_output)

        with gr.Column():
            gr.Markdown("### Список пользователей")
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    with gr.Row():
        gr.Markdown("### Удалить пользователя")
        delete_input = gr.Textbox(label="Имя пользователя для удаления")
        delete_button = gr.Button("Удалить")
        delete_output = gr.Textbox(label="Результат удаления")
        delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
