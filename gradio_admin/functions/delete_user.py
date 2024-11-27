#!/usr/bin/env python3
# delete_user.py
# Скрипт для удаления пользователей в проекте wg_qr_generator

import os
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path, check_wireguard_status

# Функция для логирования (аналог log_debug)
def log_debug(message, level="DEBUG"):
    """
    Простая функция для вывода сообщений в консоль с временем в формате с миллисекундами.
    :param message: Сообщение для вывода.
    :param level: Уровень сообщения ("INFO", "DEBUG", "ERROR").
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # Оставляем миллисекунды
    print(f"{timestamp} - {level:<8} ℹ️  {message}")

def delete_user(username):
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    :param username: Имя пользователя для удаления.
    :return: Сообщение о результате операции.
    """
    log_debug("---------- Процесс 🔥 удаления пользователя ----------", level="INFO")

    # Проверка статуса WireGuard перед началом
    wg_status = check_wireguard_status()
    if not wg_status["active"]:
        log_debug("❌ WireGuard неактивен. Удаление невозможно.", level="ERROR")
        return "❌ WireGuard неактивен. Проверьте состояние сервера."

    log_debug(f"🌐 WireGuard активен: {wg_status['status']}", level="INFO")
    log_debug(f"🛡️ Открытые порты: {wg_status['ports']}", level="INFO")

    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    log_debug(f"➡️ Начинаем удаление пользователя: '{username}'.")

    if not os.path.exists(user_records_path):
        log_debug(f"❌ Файл данных пользователей не найден: {user_records_path}", level="ERROR")
        return "❌ Ошибка: файл данных пользователей отсутствует."

    try:
        # Чтение данных пользователей
        user_data = read_json(user_records_path)
        log_debug(f"📂 Данные пользователей успешно загружены.")

        if username not in user_data:
            log_debug(f"❌ Пользователь '{username}' не найден в данных.", level="ERROR")
            return f"❌ Пользователь '{username}' не существует."

        # Удаление записи пользователя
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        write_json(user_records_path, user_data)
        log_debug(f"📝 Запись пользователя '{username}' удалена из данных.")

        # Извлечение публичного ключа пользователя
        public_key = extract_public_key(username, wg_config_path)
        if not public_key:
            log_debug(f"❌ Публичный ключ пользователя '{username}' не найден в конфигурации WireGuard.", level="ERROR")
            return f"❌ Публичный ключ пользователя '{username}' отсутствует."

        # Удаление пользователя из WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        log_debug(f"🔐 Пользователь '{username}' удален из WireGuard.")

        # Обновление конфигурации WireGuard
        remove_peer_from_config(public_key, wg_config_path, username)
        log_debug(f"✅ Конфигурация WireGuard успешно обновлена.")

        log_debug("---------- Процесс 🔥 удаления пользователя завершен ----------", level="INFO")
        return f"✅ Пользователь '{username}' успешно удалён."
    except Exception as e:
        log_debug(f"⚠️ Ошибка при удалении пользователя '{username}': {str(e)}", level="ERROR")
        return f"❌ Ошибка при удалении пользователя '{username}': {str(e)}"

def extract_public_key(username, config_path):
    """
    Извлечение публичного ключа пользователя из конфигурации WireGuard.
    :param username: Имя пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :return: Публичный ключ пользователя.
    """
    log_debug(f"🔍 Поиск публичного ключа для пользователя '{username}' в {config_path}.")
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                public_key = line.split("=", 1)[1].strip()
                log_debug(f"🔑 Найден публичный ключ для '{username}': {public_key}")
                return public_key
        log_debug(f"❌ Публичный ключ для '{username}' не найден.", level="ERROR")
        return None
    except Exception as e:
        log_debug(f"⚠️ Ошибка при поиске публичного ключа: {str(e)}", level="ERROR")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Удаление записи [Peer] и связанного комментария из конфигурационного файла WireGuard.
    Удаляет комментарий и 4 строки, начиная с него.
    :param public_key: Публичный ключ пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :param client_name: Имя клиента.
    """
    log_debug(f"🛠️ Удаление конфигурации пользователя '{client_name}' из {config_path}.")

    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0  # Счетчик строк для пропуска

        for i, line in enumerate(lines):
            # Если найден комментарий клиента
            if line.strip() == f"### Client {client_name}":
                log_debug(f"📌 Найден блок для '{client_name}' на строке {i}. Удаляем...")
                skip_lines = 5  # Удаляем 5 строк начиная с этого момента
                continue

            # Пропуск строк, связанных с удаляемым блоком
            if skip_lines > 0:
                log_debug(f"⏩ Пропуск строки {i}: {line.strip()}")
                skip_lines -= 1
                continue

            # Сохранение остальных строк
            updated_lines.append(line)

        # Запись обновленной конфигурации
        with open(config_path, "w") as f:
            f.writelines(updated_lines)

        log_debug(f"✅ Конфигурация пользователя '{client_name}' удалена.")
    except Exception as e:
        log_debug(f"⚠️ Ошибка при обновлении конфигурации: {str(e)}", level="ERROR")
