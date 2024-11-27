#!/usr/bin/env python3
# main.py
## Основной скрипт для создания пользователей WireGuard

import sys
import os
import json
from datetime import datetime
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.ip_management import generate_ip
from modules.config_writer import add_user_to_server_config
from modules.qr_generator import generate_qr_code
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
from modules.main_registration_fields import create_user_record
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

def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard и показывает его статус.
    """
    try:
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"WireGuard {interface} успешно перезапущен.")

        # Получение статуса WireGuard
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI}  {line.strip()}")

        # Вывод состояния firewall
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        logger.info(f"{FIREWALL_EMOJI}  {firewall_status.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    """
    logger.info(f"Начало генерации конфигурации для пользователя: {nickname}")
    server_public_key = params['SERVER_PUB_KEY']
    endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
    dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

    private_key = generate_private_key()
    logger.debug("Приватный ключ сгенерирован.")
    public_key = generate_public_key(private_key).decode()
    logger.debug("Публичный ключ сгенерирован.")
    preshared_key = generate_preshared_key().decode()
    logger.debug("Пресекретный ключ сгенерирован.")

    # Генерация IP-адреса
    address, new_ipv4 = generate_ip(config_file)
    logger.info(f"IP-адрес сгенерирован: {address}")

    # Генерация конфигурации клиента
    client_config = create_client_config(
        private_key=private_key,
        address=address,
        dns_servers=dns_servers,
        server_public_key=server_public_key,
        preshared_key=preshared_key,
        endpoint=endpoint
    )
    logger.debug("Конфигурация клиента создана.")

    config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
    qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

    # Сохраняем конфигурацию
    os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
    with open(config_path, "w") as file:
        file.write(client_config)
    logger.info(f"Конфигурация клиента сохранена в {config_path}")

    # Генерация QR-кода
    generate_qr_code(client_config, qr_path)
    logger.info(f"QR-код сохранён в {qr_path}")

    # Добавление пользователя в конфигурацию сервера
    add_user_to_server_config(config_file, nickname, public_key, preshared_key, address)
    logger.info("Пользователь добавлен в конфигурацию сервера.")

    return config_path, qr_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Использование: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    try:
        logger.info("Инициализация директорий.")
        setup_directories()

        logger.info("Загрузка параметров сервера.")
        params = load_params(params_file)

        logger.info("Генерация конфигурации пользователя.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ Конфигурация сохранена в {config_path}")
        logger.info(f"✅ QR-код сохранён в {qr_path}")
        restart_wireguard(params['SERVER_WG_NIC'])

    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
