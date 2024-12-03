#!/usr/bin/env python3
# wg_qr_generator/install.py
# ===========================================
# Скрипт для установки и настройки WireGuard
# ===========================================
# Назначение:
# - Установка WireGuard
# - Настройка сервера WireGuard
# - Создание первого пользователя через main.py
# - Настройка фаервола
#
# Использование:
# - Запустите скрипт из корня проекта wg_qr_generator:
#   $ python3 install.py
#
# Примечания:
# - Скрипт использует настройки из `settings.py`.
# - Все действия логируются в файл, указанный в `LOG_FILE_PATH`.
# ===========================================

import os
import shutil
import subprocess
import platform
import json
from pathlib import Path
from settings import (
    SERVER_CONFIG_FILE,
    PARAMS_FILE,
    WG_CONFIG_DIR,
    QR_CODE_DIR,
    LOG_FILE_PATH,
    LOG_LEVEL,
    WIREGUARD_PORT,
    DEFAULT_TRIAL_DAYS,
)
import logging

# Настройка логгера
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def detect_package_manager():
    """Определяет пакетный менеджер для текущей системы."""
    distro = platform.system()
    if distro == "Linux":
        with open("/etc/os-release", "r") as f:
            os_release = f.read()
            if "Ubuntu" in os_release:
                return "apt"
            elif "CentOS" in os_release or "Stream" in os_release:
                return "dnf"
    print("❌ Unsupported OS or distribution. Exiting.")
    logger.error("Unsupported OS or distribution.")
    exit(1)

def install_wireguard():
    """Устанавливает WireGuard."""
    package_manager = detect_package_manager()
    try:
        logger.info(f"Installing WireGuard using {package_manager}...")
        if package_manager == "apt":
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y", "wireguard", "wireguard-tools"], check=True)
        elif package_manager == "dnf":
            subprocess.run(["dnf", "install", "-y", "epel-release"], check=True)
            subprocess.run(["dnf", "install", "-y", "wireguard-tools"], check=True)
        print("✅ WireGuard installed successfully.")
        logger.info("WireGuard installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install WireGuard: {e}")
        print("❌ Failed to install WireGuard. Check logs for details.")
        exit(1)

def collect_user_input():
    """Собирает ввод от пользователя."""
    print("=== 🛠️  WireGuard Installation ===")
    server_ip = input("Enter server IP [auto-detect]: ").strip() or "auto-detect"
    port = input(f"Enter WireGuard port [{WIREGUARD_PORT}]: ").strip() or WIREGUARD_PORT
    subnet = input("Enter subnet for clients [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
    dns = input("Enter DNS servers [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

    return {
        "server_ip": server_ip,
        "port": port,
        "subnet": subnet,
        "dns": dns,
    }

def configure_server(server_ip, port, subnet, dns):
    """Создаёт серверную конфигурацию."""
    try:
        logger.info("Configuring server...")
        if not SERVER_CONFIG_FILE.parent.exists():
            SERVER_CONFIG_FILE.parent.mkdir(parents=True)

        private_key = subprocess.check_output(["wg", "genkey"]).strip()
        public_key = subprocess.check_output(["echo", private_key, "|", "wg", "pubkey"]).strip()

        with open(SERVER_CONFIG_FILE, "w") as config:
            config.write(f"""
[Interface]
PrivateKey = {private_key.decode()}
Address = {subnet.split('/')[0]}
ListenPort = {port}
SaveConfig = true

PostUp = firewall-cmd --zone=public --add-interface=%i
PostUp = firewall-cmd --add-port={port}/udp
PostUp = firewall-cmd --add-rich-rule="rule family=ipv4 source address={subnet} masquerade"
PostDown = firewall-cmd --zone=public --remove-interface=%i
PostDown = firewall-cmd --remove-port={port}/udp
PostDown = firewall-cmd --remove-rich-rule="rule family=ipv4 source address={subnet} masquerade"
""")

        # Save parameters
        with open(PARAMS_FILE, "w") as params:
            params.write(f"""
SERVER_PUB_IP={server_ip}
SERVER_PORT={port}
SERVER_PUB_KEY={public_key.decode()}
SERVER_PRIV_KEY={private_key.decode()}
SERVER_SUBNET={subnet}
CLIENT_DNS={dns}
""")

        print("✅ Server configured successfully.")
        logger.info("Server configuration saved.")
    except Exception as e:
        logger.error(f"Failed to configure server: {e}")
        print("❌ Failed to configure server. Check logs for details.")
        exit(1)

def setup_firewall(port, subnet):
    """Настраивает фаервол."""
    try:
        logger.info("Configuring firewall...")
        subprocess.run(["firewall-cmd", "--zone=public", "--add-port", f"{port}/udp"], check=True)
        subprocess.run(["firewall-cmd", "--permanent", "--add-rich-rule", f"rule family=ipv4 source address={subnet} masquerade"], check=True)
        print("✅ Firewall configured successfully.")
        logger.info("Firewall configured successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to configure firewall: {e}")
        print("❌ Failed to configure firewall. Check logs for details.")

def create_initial_user():
    """Создаёт первого пользователя через main.py."""
    try:
        logger.info("Creating initial user...")
        subprocess.run(["python3", "main.py", "SetupUser"], check=True)
        print("✅ Initial user created successfully.")
        logger.info("Initial user created successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create initial user: {e}")
        print("❌ Failed to create initial user. Check logs for details.")

def start_wireguard():
    """Запускает WireGuard."""
    try:
        subprocess.run(["systemctl", "start", "wg-quick@wg0"], check=True)
        print("✅ WireGuard started successfully.")
        logger.info("WireGuard started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start WireGuard: {e}")
        print("❌ Failed to start WireGuard. Check logs for details.")

def main():
    """Основная функция установки."""
    if shutil.which("wg"):
        print("⚠️ WireGuard is already installed. Do you want to reinstall it? (yes/no): ", end="")
        if input().strip().lower() != "yes":
            print("❌ Installation cancelled.")
            return

    # Установка WireGuard
    install_wireguard()

    # Сбор параметров
    params = collect_user_input()

    # Настройка сервера
    configure_server(**params)

    # Настройка фаервола
    setup_firewall(params["port"], params["subnet"])

    # Создание первого пользователя
    create_initial_user()

    # Запуск WireGuard
    start_wireguard()

    print("🎉 WireGuard installation complete!")

if __name__ == "__main__":
    main()
