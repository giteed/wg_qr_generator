#!/usr/bin/env python3
# wg_qr_generator/uninstall.py
# ===========================================
# Скрипт для удаления WireGuard
# ===========================================
# Назначение:
# - Останавливает службу WireGuard
# - Удаляет конфигурационные файлы и директории
# - Удаляет правила фаервола, связанные с WireGuard
# - Удаляет WireGuard из системы
# - Сохраняет резервные копии конфигураций перед удалением (по запросу)
#
# Использование:
# - Запустите скрипт из корня проекта wg_qr_generator:
#   $ python3 uninstall.py
#
# Примечания:
# - Для работы скрипт требует настройки `settings.py`
# - Все действия логируются в файл, указанный в `LOG_FILE_PATH` из `settings.py`
# ===========================================
# Автор: [Ваше имя или название команды]
# Версия: 1.0
# Дата: 2024-12-03
# ===========================================

import os
import subprocess
import shutil
import logging
from pathlib import Path

# Import project settings
try:
    from settings import (
        SERVER_CONFIG_FILE,
        PARAMS_FILE,
        WG_CONFIG_DIR,
        LOG_FILE_PATH,
        LOG_LEVEL,
        LOG_DIR,
    )
except ImportError:
    print("❌ Could not import settings. Ensure this script is run from the project root.")
    exit(1)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def stop_wireguard():
    """Stop WireGuard service."""
    try:
        logger.info("Stopping WireGuard service...")
        subprocess.run(["systemctl", "stop", "wg-quick@wg0"], check=True)
        logger.info("WireGuard service stopped.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to stop WireGuard service: %s", e)
        print("❌ Failed to stop WireGuard service. Check logs for details.")
        return False
    return True

def remove_config_files():
    """Remove WireGuard configuration files."""
    try:
        if SERVER_CONFIG_FILE.exists():
            SERVER_CONFIG_FILE.unlink()
            logger.info(f"Removed server config file: {SERVER_CONFIG_FILE}")
        if PARAMS_FILE.exists():
            PARAMS_FILE.unlink()
            logger.info(f"Removed params file: {PARAMS_FILE}")
        if WG_CONFIG_DIR.exists():
            shutil.rmtree(WG_CONFIG_DIR)
            logger.info(f"Removed WireGuard user config directory: {WG_CONFIG_DIR}")
        print("✅ Configuration files removed.")
    except Exception as e:
        logger.error("Failed to remove configuration files: %s", e)
        print("❌ Failed to remove configuration files. Check logs for details.")

def remove_firewall_rules():
    """Remove firewall rules associated with WireGuard."""
    try:
        logger.info("Removing WireGuard firewall rules...")
        subprocess.run(["firewall-cmd", "--zone=public", "--remove-interface=wg0"], check=True)
        subprocess.run(["firewall-cmd", "--remove-port=51820/udp"], check=True)
        print("✅ Firewall rules removed.")
        logger.info("Firewall rules removed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to remove firewall rules: %s", e)
        print("❌ Failed to remove firewall rules. Check logs for details.")

def uninstall_wireguard():
    """Uninstall WireGuard."""
    try:
        logger.info("Uninstalling WireGuard...")
        subprocess.run(["apt", "remove", "-y", "wireguard"], check=True)
        subprocess.run(["apt", "autoremove", "-y"], check=True)
        print("✅ WireGuard uninstalled successfully.")
        logger.info("WireGuard uninstalled successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to uninstall WireGuard: %s", e)
        print("❌ Failed to uninstall WireGuard. Check logs for details.")

def confirm_action():
    """Ask for user confirmation before proceeding."""
    while True:
        choice = input("Are you sure you want to uninstall WireGuard? (yes/no): ").strip().lower()
        if choice in ["yes", "no"]:
            return choice == "yes"
        print("Please answer 'yes' or 'no'.")

def save_backup():
    """Save backup of configurations."""
    backup_dir = Path("wireguard_backup")
    if not backup_dir.exists():
        backup_dir.mkdir()
    try:
        if SERVER_CONFIG_FILE.exists():
            shutil.copy(SERVER_CONFIG_FILE, backup_dir / "wg0.conf")
        if PARAMS_FILE.exists():
            shutil.copy(PARAMS_FILE, backup_dir / "params")
        if WG_CONFIG_DIR.exists():
            shutil.copytree(WG_CONFIG_DIR, backup_dir / "wg_configs")
        print(f"✅ Backup saved in {backup_dir}")
        logger.info(f"Backup saved successfully in {backup_dir}")
    except Exception as e:
        logger.error("Failed to save backup: %s", e)
        print("❌ Failed to save backup. Check logs for details.")

def main():
    """Main function to uninstall WireGuard."""
    print("=== 🗑️  Uninstall WireGuard ===")
    if not confirm_action():
        print("❌ Uninstallation cancelled.")
        return
    save_choice = input("Do you want to save a backup of the configurations? (yes/no): ").strip().lower()
    if save_choice == "yes":
        save_backup()
    if stop_wireguard():
        remove_config_files()
        remove_firewall_rules()
        uninstall_wireguard()
    print("🎉 WireGuard uninstallation complete!")

if __name__ == "__main__":
    main()
