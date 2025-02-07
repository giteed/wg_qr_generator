#!/usr/bin/env python3
# modules/report_utils.py
# ===========================================
# Модуль для работы с отчетами проекта wg_qr_generator
# ===========================================
# Этот модуль предоставляет функции для генерации и отображения отчетов,
# включая полный отчет, краткий отчет, обобщённый отчет и информацию о состоянии проекта.
#
# Версия: 2.1
# Обновлено: 2024-12-10

import os
import json
import subprocess
import platform
import psutil
import time
from datetime import datetime
from termcolor import colored
from pathlib import Path
from modules.firewall_utils import get_external_ip
from settings import SUMMARY_REPORT_PATH, TEST_REPORT_PATH
from modules.test_report_generator import generate_report

# Путь к скрипту создания summary_report
SUMMARY_SCRIPT = Path(__file__).resolve().parent.parent / "ai_diagnostics" / "ai_diagnostics_summary.py"


from datetime import datetime, timedelta

def create_summary_report():
    """Проверяет свежесть отчета и вызывает скрипт для создания summary_report.txt при необходимости."""
    try:
        # Проверка существования файла
        if SUMMARY_REPORT_PATH.exists():
            # Получаем время последнего изменения файла
            last_modified = datetime.fromtimestamp(SUMMARY_REPORT_PATH.stat().st_mtime)
            age = datetime.now() - last_modified

            if age < timedelta(minutes=1):
                print(f" ✅ Файл {SUMMARY_REPORT_PATH} актуален. Пересоздание не требуется.")
                return
            else:
                print(f" ⏳ Файл {SUMMARY_REPORT_PATH} устарел ({age.seconds // 60} минут). Пересоздаю...")

        else:
            print(f" ⏳ Файл {SUMMARY_REPORT_PATH} отсутствует. Создаю...")

        # Явный вызов через Python
        subprocess.run(["python3", str(SUMMARY_SCRIPT)], check=True)
        
        print(f" ✅ Файл {SUMMARY_REPORT_PATH} успешно создан.")
    except subprocess.CalledProcessError as e:
        print(f" ❌ Ошибка выполнения скрипта {SUMMARY_SCRIPT}: {e}")
    except Exception as e:
        print(f" ❌ Непредвиденная ошибка при создании файла {SUMMARY_REPORT_PATH}: {e}")


def get_open_ports():
    """Возвращает список открытых портов в firewalld."""
    try:
        output = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"], text=True)
        return output.strip() if output else colored("Нет открытых портов ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Ошибка получения данных ❌", "red")


def get_wireguard_status():
    """Возвращает статус WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "is-active", "wg-quick@wg0"], text=True).strip()
        if output == "active":
            return colored("активен ✅", "green")
        return colored("неактивен ❌", "red")
    except subprocess.CalledProcessError:
        return colored("не установлен ❌", "red")


def get_wireguard_peers():
    """Получает список активных пиров WireGuard."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
        peers = [line.split(":")[1].strip() for line in output if line.startswith("peer:")]
        if peers:
            return f"{len(peers)} активных пиров ✅"
        return colored("Нет активных пиров ❌", "red")
    except FileNotFoundError:
        return colored("Команда 'wg' не найдена ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Ошибка получения данных ❌", "red")


def get_users_data():
    """Получает информацию о пользователях из user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    try:
        with open(user_records_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return colored("Файл user_records.json отсутствует ❌", "red")
    except json.JSONDecodeError:
        return colored("Файл user_records.json поврежден ❌", "red")


def get_gradio_status(port=7860):
    """Проверяет статус Gradio."""
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "gradio" in " ".join(cmdline) and str(port) in " ".join(cmdline):
                return f"запущен (PID {proc.info['pid']}) ✅"
        return colored("не запущен ❌", "red")
    except Exception as e:
        return colored(f"Ошибка проверки Gradio: {e} ❌", "red")


def get_gradio_port_status(port=7860):
    """Проверяет, открыт ли порт Gradio."""
    open_ports = get_open_ports()
    if f"{port}/tcp" in open_ports:
        return colored("открыт ✅", "green")
    return colored("закрыт ❌", "red")


def show_project_status():
    """Отображает состояние проекта."""
    print("=== Сводка состоянии проекта ===\n")

    # Информация о системе
    print(f" 🖥️   ОС: {platform.system()} {platform.release()}")
    print(f" 🧰  Ядро: {platform.uname().release}")
    print(f" 🌍  Внешний IP-адрес: {get_external_ip()}")

    # Состояние WireGuard
    print(f" 🛡️   WireGuard статус: {get_wireguard_status()}")
    config_path = "/etc/wireguard/wg0.conf"
    print(f" ⚙️   Файл конфигурации: {config_path if os.path.exists(config_path) else colored('отсутствует ❌', 'red')}")
    print(f" 🌐  Активные peers: {get_wireguard_peers()}")

    # Последний отчёт
    report_path = os.path.join("wg_qr_generator", "test_report.txt")
    if os.path.exists(report_path):
        print(f" 📋  Последний отчет: {report_path}")
    else:
        print(colored(" 📋  Последний отчет: отсутствует ❌", "red"))

    print("\n===========================================\n")


def generate_project_report():
    """Генерация полного отчета."""
    print("\n  📋  Запуск генерации полного отчета...")
    try:
        generate_report()
    except Exception as e:
        print(f" ❌ Ошибка при генерации полного отчета: {e}")


def display_test_report():
    """Вывод содержимого полного отчета в консоль."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            print(file.read())
    else:
        print(f"  ❌  Файл полного отчета не найден: {TEST_REPORT_PATH}")


def display_test_summary():
    """Вывод краткого отчета."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            summary_keys = [
                "Дата и время",
                "WireGuard статус",
                "Gradio",
                "Открытые порты",
                "wg0.conf"
            ]
            print("\n=== Краткий отчет о состоянии проекта ===")
            for line in lines:
                if any(key in line for key in summary_keys):
                    print(line.strip())
            print("\n=========================================\n")
    else:
        print(f"  ❌  Файл отчета о состоянии проекта wg_qr_generator не найден: {TEST_REPORT_PATH}")


def display_summary_report():
    """
    Читает и выводит содержимое отчета о состоянии проекта wg_qr_generator.
    Использует путь к файлу из settings.py.
    Если файл отсутствует, инициирует его создание.
    """
    try:
        if not SUMMARY_REPORT_PATH.exists():
            create_summary_report()

        with open(SUMMARY_REPORT_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        print("\n=== 📋 Отчет о состоянии проекта wg_qr_generator ===\n")
        print(content)

    except Exception as e:
        print(f" ❌ Ошибка при чтении отчета о состоянии проекта wg_qr_generator: {e}")


if __name__ == "__main__":
    show_project_status()
    time.sleep(2)
    print("\n=== Выполнение работы с отчетами ===\n")
    display_summary_report()
