#!/usr/bin/env python3
# modules/gradio_utils.py

import os
import subprocess
from gradio_admin.main_interface import admin_interface


def check_and_open_port(port):
    """Проверяет, открыт ли порт, и открывает его через firewalld."""
    try:
        # Проверяем открытые порты
        result = subprocess.run(
            ["firewall-cmd", "--list-ports"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if str(port) + "/tcp" not in result.stdout:
            subprocess.run(["firewall-cmd", "--add-port", f"{port}/tcp"], check=True)
            subprocess.run(["firewall-cmd", "--runtime-to-permanent"], check=True)
            print(f"✅ Порт {port} открыт.")
        else:
            print(f"ℹ️ Порт {port} уже открыт.")
    except Exception as e:
        print(f"❌ Ошибка при настройке порта {port}: {e}")


def run_gradio_admin_interface():
    """Запускает интерфейс Gradio на указанном порту."""
    port = 7860
    check_and_open_port(port)
    print(f"🌐 Запуск Gradio интерфейса на http://0.0.0.0:{port}")
    admin_interface.launch(server_name="0.0.0.0", server_port=port, share=True)
