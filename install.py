#!/usr/bin/env python3
# wg_qr_generator/install.py
# ===========================================
# Скрипт для установки и настройки WireGuard
# ===========================================

import os
import shutil
import subprocess
import platform
import time
from pathlib import Path
from settings import (
    SERVER_CONFIG_FILE,
    PARAMS_FILE,
    WIREGUARD_PORT,
    PRINT_SPEED,
    DEFAULT_TRIAL_DAYS,
)
from ai_diagnostics.ai_diagnostics import display_message_slowly
from modules.firewall_utils import get_external_ip
import logging

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s ℹ️  %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def display_message(message, print_speed=None, end="\n"):
    """Вывод сообщения с имитацией печати."""
    display_message_slowly(f"    {message}", print_speed=print_speed)
    if end:
        print(end, end="")

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
    display_message("❌ Unsupported OS or distribution. Exiting.")
    logger.error("Unsupported OS or distribution.")
    exit(1)

def install_wireguard():
    """Устанавливает WireGuard с индикатором выполнения."""
    package_manager = detect_package_manager()
    display_message("🍀 Installing WireGuard...")
    try:
        time.sleep(1)  # Имитация выполнения
        if package_manager == "apt":
            subprocess.run(["apt", "update"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["apt", "install", "-y", "wireguard", "wireguard-tools"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif package_manager == "dnf":
            subprocess.run(["dnf", "install", "-y", "epel-release"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["dnf", "install", "-y", "wireguard-tools"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        display_message("✅ WireGuard installed successfully!\n")
        logger.info("WireGuard installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install WireGuard: {e}")
        display_message("❌ Failed to install WireGuard. Check logs for details.")
        exit(1)

def collect_user_input():
    """Собирает ввод от пользователя с креативными подсказками."""
    display_message("=== 🛠️  WireGuard Installation ===")
    display_message("Let's set up your WireGuard server!\n")

    external_ip = get_external_ip()
    display_message(f"- 🌐 Detected external IP: {external_ip}\n")

    server_ip = input(" 🌍 Enter server IP [auto-detect]: ").strip() or external_ip
    port = input(" 🔒 Enter WireGuard port [51820]: ").strip() or WIREGUARD_PORT
    subnet = input(" 📡 Enter subnet for clients [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
    dns = input(" 🧙‍♂️ Enter DNS servers [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

    return {
        "server_ip": server_ip,
        "port": port,
        "subnet": subnet,
        "dns": dns,
    }

def configure_server(server_ip, port, subnet, dns):
    """Создаёт серверную конфигурацию."""
    try:
        display_message("🔧 Configuring WireGuard server...")
        private_key = subprocess.check_output(["wg", "genkey"]).strip()
        public_key = subprocess.check_output(["wg", "pubkey"], input=private_key).strip()

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

        with open(PARAMS_FILE, "w") as params:
            params.write(f"""
SERVER_PUB_IP={server_ip}
SERVER_PORT={port}
SERVER_PUB_KEY={public_key.decode()}
SERVER_PRIV_KEY={private_key.decode()}
SERVER_SUBNET={subnet}
CLIENT_DNS={dns}
""")
        display_message("✅ Server configuration saved!")
        logger.info("Server configuration saved.")
    except Exception as e:
        logger.error(f"Failed to configure server: {e}")
        display_message("❌ Failed to configure server. Please check the logs for details.")

def create_initial_user():
    """Создаёт первого пользователя через main.py."""
    try:
        display_message("🌱 Creating the initial user (SetupUser)...")
        subprocess.run(["python3", "main.py", "SetupUser"], check=True)
        display_message("✅ Initial user created successfully!")
        logger.info("Initial user created successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create initial user: {e}")
        display_message("❌ Failed to create initial user. Check logs for details.")

def start_wireguard():
    """Запускает WireGuard."""
    try:
        display_message("🚀 Starting WireGuard...")
        subprocess.run(["systemctl", "start", "wg-quick@wg0"], check=True)
        display_message("✅ WireGuard started successfully!")
        logger.info("WireGuard started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start WireGuard: {e}")
        display_message("❌ Failed to start WireGuard. Check logs for details.")

def main():
    """Основная функция установки."""
    if shutil.which("wg"):
        display_message("⚠️  WireGuard is already installed!")
        reinstall = input("⚠️  Do you want to reinstall it? (yes/no): ").strip().lower()
        if reinstall != "yes":
            display_message("❌ Installation cancelled.")
            return

    install_wireguard()
    params = collect_user_input()
    configure_server(**params)
    create_initial_user()
    start_wireguard()
    display_message("🎉 WireGuard installation complete!")

if __name__ == "__main__":
    main()
