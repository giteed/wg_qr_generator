#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 5.1
# Обновлено: 2024-12-02

import json
import time
import sys
import subprocess
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
DIAGNOSTICS_DIR = PROJECT_ROOT / "ai_diagnostics"

sys.path.append(str(PROJECT_ROOT))  # Добавляем путь к корню проекта
sys.path.append(str(MODULES_DIR))  # Добавляем путь к модулям

# Импорт из настроек
from settings import (
    DEBUG_REPORT_PATH,
    TEST_REPORT_PATH,
    MESSAGES_DB_PATH,
    PROJECT_DIR,
    LOG_LEVEL,
    LOG_FILE_PATH,
    ANIMATION_SPEED,
    PRINT_SPEED,
    LINE_DELAY,
    GRADIO_PORT,
)

# Импорт функции для подсети WireGuard
from utils import get_wireguard_subnet

# Настраиваем logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Проверяемые порты
WIREGUARD_PORT = 51820
REQUIRED_PORTS = [f"{WIREGUARD_PORT}/udp", f"{GRADIO_PORT}/tcp"]

# Скрипты
SUMMARY_SCRIPT = DIAGNOSTICS_DIR / "ai_diagnostics_summary.py"


def run_command(command):
    """Запускает внешнюю команду и возвращает её результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении команды '{' '.join(command)}': {e.stderr.strip()}")
        return None


def check_ports():
    """Проверяет состояние необходимых портов с выводом отладки."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return []

    logger.debug(f"Результат команды проверки фаервола:\n{result}")

    open_ports = []
    for line in result.splitlines():
        if "ports:" in line:
            try:
                ports_line = line.split("ports:")[1].strip()
                open_ports.extend(port.strip() for port in ports_line.split())
            except IndexError:
                logger.warning("Не удалось обработать строку портов.")
                continue

    closed_ports = [port for port in REQUIRED_PORTS if port not in open_ports]
    return closed_ports


def check_masquerade_rules():
    """Проверяет наличие правил маскарадинга для WireGuard."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return ["Ошибка: не удалось выполнить команду для проверки маскарадинга."]

    logger.debug(f"Результат команды проверки маскарадинга:\n{result}")

    try:
        # Получаем подсеть из конфигурации WireGuard
        wireguard_subnet = get_wireguard_subnet()
        ipv4_network = wireguard_subnet.split("/")[0].rsplit(".", 1)[0] + ".0/24"
        ipv6_rule = 'rule family="ipv6" source address="fd42:42:42::0/24" masquerade'
        required_rules = [
            f'rule family="ipv4" source address="{ipv4_network}" masquerade',
            ipv6_rule
        ]
    except Exception as e:
        logger.error(f"Ошибка при извлечении подсети WireGuard: {e}")
        return ["Ошибка: не удалось определить необходимые правила маскарадинга."]

    # Проверяем наличие правил
    missing_rules = []
    for rule in required_rules:
        if rule not in result:
            missing_rules.append(rule)

    logger.debug(f"Отсутствующие правила маскарадинга: {missing_rules}")
    return missing_rules


def check_gradio_status():
    """Проверяет, запущен ли Gradio на порту."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    if not result:
        return False

    logger.debug(f"Результат команды проверки Gradio:\n{result}")

    for line in result.splitlines():
        if f":{GRADIO_PORT} " in line and "LISTEN" in line:
            return True
    return False


def parse_reports(messages_db_path):
    """Парсер для анализа отчетов."""
    try:
        with open(messages_db_path, "r", encoding="utf-8") as db_file:
            messages_db = json.load(db_file)
    except FileNotFoundError:
        logger.error(f" ❌ Файл messages_db.json не найден: {messages_db_path}")
        return [], []

    findings = []
    suggestions = []

    closed_ports = check_ports()
    if closed_ports:
        findings.append(messages_db["ports_closed"])

    missing_masquerade_rules = check_masquerade_rules()
    if missing_masquerade_rules:
        findings.append({
            "title": "🔒 Проблемы с маскарадингом",
            "message": f"Следующие правила маскарадинга отсутствуют:\n{', '.join(missing_masquerade_rules)}",
            "commands": ["sudo systemctl restart wg-quick@wg0"]
        })

    if not check_gradio_status():
        suggestions.append(messages_db["gradio_not_running"])

    return findings, suggestions


def display_message_slowly(message):
    """Имитация печати ИИ."""
    for line in message.split("\n"):
        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            time.sleep(PRINT_SPEED)
        print()
        time.sleep(LINE_DELAY)


def handle_findings(findings):
    """Обрабатывает обнаруженные проблемы."""
    for finding in findings:
        title = finding["title"]
        message = finding["message"]
        commands = finding.get("commands", [])

        display_message_slowly(f"\n   {title}\n   {'=' * (len(title) + 2)}\n")
        display_message_slowly(message)

        if commands:
            display_message_slowly("\n 🛠  Найдены команды для устранения проблемы. Попробовать выполнить их автоматически? (y/n): ")
            user_input = input().strip().lower()
            if user_input == "y":
                display_message_slowly(" ⚙️  Выполняю команды...")
                results = execute_commands(commands)
                display_message_slowly(f"\n 📝  Результат выполнения команд:\n{results}")


def main():
    """Основной запуск программы."""
    logger.info("Начало выполнения диагностики.")
    display_message_slowly("\n 🎯  Вот что мы обнаружили:")

    findings, suggestions = parse_reports(MESSAGES_DB_PATH)

    if findings:
        handle_findings(findings)

    if suggestions:
        for suggestion in suggestions:
            display_message_slowly(f"\n {suggestion['title']}\n {suggestion['message']}")

    if not findings and not suggestions:
        display_message_slowly(" ✅  Всё выглядит хорошо!\n 👍  Проблем не обнаружено.")

    print("\n")
    subprocess.run([sys.executable, str(SUMMARY_SCRIPT)])


if __name__ == "__main__":
    main()
