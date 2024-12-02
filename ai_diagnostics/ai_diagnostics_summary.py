#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics_summary.py
# Скрипт для создания обобщенного отчета о состоянии проекта wg_qr_generator.
# Версия: 1.1
# Обновлено: 2024-12-02
# Включает проверку портов, статуса WireGuard и фаервола.

import os
import subprocess
from pathlib import Path

# Пути для отчетов
LOG_DIR = Path("/root/pyWGgen/user/data/logs")
SUMMARY_REPORT_PATH = LOG_DIR / "summary_report.txt"
DEBUG_REPORT_PATH = Path("/root/pyWGgen/wg_qr_generator/ai_diagnostics/debug_report.txt")
TEST_REPORT_PATH = Path("/root/pyWGgen/wg_qr_generator/ai_diagnostics/test_report.txt")
PROJECT_DIR = Path("/root/pyWGgen/wg_qr_generator")

# Проверяем наличие путей
LOG_DIR.mkdir(parents=True, exist_ok=True)


def run_command(command):
    """Выполняет команду в терминале и возвращает результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.stderr.strip()}"


def check_ports():
    """Проверяет открытые порты."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    open_ports = []
    for line in result.splitlines():
        if ":51820" in line:
            open_ports.append("51820 (WireGuard)")
        if ":7860" in line:
            open_ports.append("7860 (Gradio)")
    return open_ports


def check_firewall():
    """Проверяет состояние фаервола и список открытых портов."""
    command_status = ["firewall-cmd", "--state"]
    command_ports = ["firewall-cmd", "--list-ports"]
    status = run_command(command_status)
    if status != "running":
        return f"Фаервол: {status}", []
    open_ports = run_command(command_ports).split()
    return f"Фаервол: Активен", open_ports


def check_wireguard_status():
    """Проверяет состояние WireGuard."""
    command_status = ["systemctl", "is-active", "wg-quick@wg0.service"]
    command_peers = ["wg", "show"]
    status = run_command(command_status)
    wg_info = run_command(command_peers) if status == "active" else "WireGuard не активен."
    return status, wg_info


def generate_summary():
    """Создает обобщенный отчет."""
    print(" 🤖 Создание обобщенного отчета...")
    
    # Проверка пользователей
    total_users = 0
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            content = file.read()
            total_users = content.count("peer")  # Подсчет peer как пользователей
    
    # Проверка WireGuard
    wg_status, wg_info = check_wireguard_status()
    peers_count = wg_info.count("peer:") if "peer:" in wg_info else 0
    
    # Проверка портов
    open_ports = check_ports()
    
    # Проверка фаервола
    firewall_status, firewall_ports = check_firewall()
    
    # Формируем отчет
    summary = [
        "=== 📋 Обобщенный отчет о состоянии проекта ===",
        "\n📂 Пользователи:",
        f"- Общее количество пользователей: {total_users}",
        "\n🔒 WireGuard:",
        f"- Общее количество peer: {peers_count}",
        f"- Статус WireGuard: {wg_status}",
        f"- Информация о WireGuard:\n{wg_info if wg_status == 'active' else ''}",
        "\n🌐 Gradio:",
        f"- Статус: {'Не запущен' if '7860 (Gradio)' not in open_ports else 'Запущен'}",
        "  - Для запуска:",
        f"    1️⃣ Перейдите в директорию проекта: cd {PROJECT_DIR}",
        "    2️⃣ Выполните команду: python3 main.py",
        "\n🔥 Фаервол:",
        f"- {firewall_status}",
        "- Открытые порты:",
        f"  - {', '.join(firewall_ports) if firewall_ports else 'Нет открытых портов'}",
        "\n🎯 Рекомендации:",
        "- Убедитесь, что количество peer совпадает с количеством пользователей.",
        "- Если Gradio не запущен, выполните предложенные действия.",
        "- Проверьте, что порты для Gradio и WireGuard доступны через фаервол."
    ]
    
    with open(SUMMARY_REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(summary))
    
    print(f" ✅ Обобщенный отчет сохранен: {SUMMARY_REPORT_PATH}")


if __name__ == "__main__":
    generate_summary()
