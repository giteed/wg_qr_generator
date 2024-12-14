#!/usr/bin/env python3
# main.py
## Основной скрипт для создания пользователей WireGuard

import sys
import os
import json
import ipaddress
from datetime import datetime
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.config_writer import add_user_to_server_config
from modules.qr_generator import generate_qr_code
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
from modules.main_registration_fields import create_user_record  # Импорт новой функции
import subprocess
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)-8s %(message)s",
    handlers=[logging.StreamHandler()]
)

DEBUG_EMOJI = "🐛"
INFO_EMOJI = "ℹ️"
WARNING_EMOJI = "⚠️"
ERROR_EMOJI = "❌"
WG_EMOJI = "🌐"
FIREWALL_EMOJI = "🛡️"

class EmojiLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if kwargs.get('level', logging.INFO) == logging.DEBUG:
            msg = f"{DEBUG_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.INFO:
            msg = f"{INFO_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.WARNING:
            msg = f"{WARNING_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.ERROR:
            msg = f"{ERROR_EMOJI}  {msg}"
        return msg, kwargs

logger = EmojiLoggerAdapter(logging.getLogger(__name__), {})

def load_existing_users():
    """
    Загружает список существующих пользователей из базы данных.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    logger.debug(f"Загрузка базы пользователей из {user_records_path}")
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.info(f"Успешно загружено {len(user_data)} пользователей.")
                return {user.lower(): user_data[user] for user in user_data}  # Нормализуем имена
            except json.JSONDecodeError as e:
                logger.warning(f"Ошибка чтения базы данных: {e}. Возвращаем пустую базу.")
                return {}
    logger.warning(f"Файл базы данных {user_records_path} не найден.")
    return {}

def is_user_in_server_config(nickname, config_file):
    """
    Проверяет наличие пользователя в конфигурации сервера.
    """
    nickname_lower = nickname.lower()
    logger.debug(f"Проверка наличия пользователя {nickname} в конфигурации {config_file}.")
    try:
        with open(config_file, "r") as file:
            for line in file:
                if nickname_lower in line.lower():
                    logger.info(f"Пользователь {nickname} найден в конфигурации сервера.")
                    return True
    except FileNotFoundError:
        logger.warning(f"Файл конфигурации {config_file} не найден.")
    return False

def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard и показывает его статус.
    """
    try:
        logger.info(f"Перезапуск интерфейса WireGuard: {interface}")
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"{WG_EMOJI} WireGuard интерфейс {interface} успешно перезапущен.")

        # Получение статуса WireGuard
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI} Статус WireGuard: {line.strip()}")

        # Вывод состояния firewall
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        for line in firewall_status.splitlines():
            logger.info(f"{FIREWALL_EMOJI} Состояние firewall: {line.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")

def validate_params(params, required_keys):
    """
    Проверяет наличие всех обязательных ключей в параметрах.
    """
    logger.debug("Проверка наличия всех необходимых ключей в параметрах.")
    missing_keys = [key for key in required_keys if key not in params]
    if missing_keys:
        logger.error(f"Отсутствуют ключи: {missing_keys}")
        raise KeyError(
            f"Отсутствуют обязательные параметры: {missing_keys}. "
            f"Проверьте файл конфигурации."
        )

def generate_next_ip(config_file, subnet="10.66.66.0/24"):
    """
    Генерирует следующий доступный IP-адрес в подсети.
    """
    logger.debug(f"Ищем свободный IP-адрес в подсети {subnet}.")
    existing_ips = []
    if os.path.exists(config_file):
        logger.debug(f"Чтение существующих IP-адресов из файла {config_file}.")
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("AllowedIPs"):
                    ip = line.split("=")[1].strip().split("/")[0]
                    existing_ips.append(ip)
    network = ipaddress.ip_network(subnet)
    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str not in existing_ips and not ip_str.endswith(".0") and not ip_str.endswith(".1") and not ip_str.endswith(".255"):
            logger.debug(f"Свободный IP-адрес найден: {ip_str}")
            return ip_str
    logger.error("Нет доступных IP-адресов в указанной подсети.")
    raise ValueError("Нет доступных IP-адресов в указанной подсети.")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    """
    logger.info("+--------- Процесс 🌱 создания пользователя активирован ---------+")
    try:
        logger.info(f"Начало генерации конфигурации для пользователя: {nickname}")
        server_public_key = params['SERVER_PUB_KEY']
        endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
        dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

        private_key = generate_private_key()
        logger.debug("Приватный ключ успешно сгенерирован.")
        public_key = generate_public_key(private_key)
        logger.debug("Публичный ключ успешно сгенерирован.")
        preshared_key = generate_preshared_key()
        logger.debug("Пресекретный ключ успешно сгенерирован.")

        # Генерация IP-адреса
        new_ipv4 = generate_next_ip(config_file, params.get('SERVER_SUBNET', '10.66.66.0/24'))
        logger.info(f"Новый IP-адрес пользователя: {new_ipv4}")

        # Генерация конфигурации клиента
        client_config = create_client_config(
            private_key=private_key,
            address=new_ipv4,
            dns_servers=dns_servers,
            server_public_key=server_public_key,
            preshared_key=preshared_key,
            endpoint=endpoint
        )
        logger.debug("Конфигурация клиента успешно создана.")

        config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
        qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

        # Сохраняем конфигурацию
        os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
        with open(config_path, "w") as file:
            file.write(client_config)
        logger.info(f"Конфигурация пользователя сохранена в {config_path}")

        # Генерация QR-кода
        generate_qr_code(client_config, qr_path)
        logger.info(f"QR-код пользователя сохранён в {qr_path}")

        # Добавление пользователя в конфигурацию сервера
        add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), new_ipv4)
        logger.info("Пользователь успешно добавлен в конфигурацию сервера.")

        return config_path, qr_path
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Использование: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    logger.info("Запуск процесса создания нового пользователя WireGuard.")
    try:
        logger.info("Инициализация директорий.")
        setup_directories()

        logger.info(f"Загрузка параметров из файла: {params_file}")
        params = load_params(params_file)

        # Валидация ключей
        required_keys = [
            'SERVER_PUB_KEY', 'SERVER_PUB_IP', 'SERVER_PORT',
            'CLIENT_DNS_1', 'CLIENT_DNS_2', 'SERVER_SUBNET', 'SERVER_WG_NIC'
        ]
        validate_params(params, required_keys)

        logger.info("Проверка существующего пользователя.")
        existing_users = load_existing_users()
        if nickname.lower() in existing_users:
            logger.error(f"Пользователь с именем '{nickname}' уже существует в базе данных.")
            sys.exit(1)

        if is_user_in_server_config(nickname, settings.SERVER_CONFIG_FILE):
            logger.error(f"Пользователь с именем '{nickname}' уже существует в конфигурации сервера.")
            sys.exit(1)

        logger.info("Генерация конфигурации пользователя.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ Конфигурация пользователя сохранена в {config_path}")
        logger.info(f"✅ QR-код пользователя сохранён в {qr_path}")
    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {e}")
    except KeyError as e:
        logger.error(f"Отсутствует ключ в параметрах: {e}")
    except ValueError as e:
        logger.error(f"Ошибка в значении параметров: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
