import os
from pathlib import Path

# Определяем базовый путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent  # Путь к корню проекта

# Пути к файлам и директориям
WG_CONFIG_DIR = BASE_DIR / "user/data/wg_configs"
QR_CODE_DIR = BASE_DIR / "user/data/qrcodes"
STALE_CONFIG_DIR = BASE_DIR / "user/data/usr_stale_config"
USER_DB_PATH = BASE_DIR / "user/data/user_records.json"
IP_DB_PATH = BASE_DIR / "user/data/ip_records.json"
SERVER_CONFIG_FILE = "/etc/wireguard/wg0.conf"  # Путь к конфигурационному файлу сервера WireGuard
PARAMS_FILE = "/etc/wireguard/params"           # Путь к файлу с параметрами WireGuard

# Параметры WireGuard
DEFAULT_TRIAL_DAYS = 30                          # Базовый срок действия аккаунта в днях

# Настройки для логирования
LOG_FILE_PATH = BASE_DIR / "user/data/logs/app.log"
LOG_LEVEL = "INFO"

# Путь к журналу диагностики
DIAGNOSTICS_LOG = BASE_DIR / "user/data/logs/diagnostics.log"

# Пути к отчетам
DEBUG_REPORT_PATH = BASE_DIR / "debug_report.txt"  # Путь к отчету диагностики
TEST_REPORT_PATH = BASE_DIR / "test_report.txt"    # Путь к отчету тестирования
MESSAGES_DB_PATH = BASE_DIR / "ai_diagnostics/messages_db.json"  # Путь к базе сообщений
