#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator
# Этот скрипт автоматически устанавливает проект, настраивает виртуальное окружение и предоставляет удобное меню для управления.

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv"
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

echo "=== Установка проекта wg_qr_generator ==="

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo "❌ Git не установлен. Установите его и повторите попытку."
  exit 1
fi

# Проверяем наличие Python 3.8+
if ! command -v python3 &>/dev/null; then
  echo "❌ Python3 не установлен. Установите его и повторите попытку."
  exit 1
fi

# Проверяем версию Python3
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info >= (3, 8))')
if [ "$PYTHON_VERSION" != "True" ]; then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии 3.8 или выше обнаружен."
fi



# Клонируем или обновляем репозиторий
cd ..
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO"
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull
fi

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR"
fi

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate"

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  pip install -r "$PROJECT_DIR/requirements.txt"
else
  echo "⚠️ Файл requirements.txt не найден. Проверьте проект."
fi

echo "✅ Установка завершена. Проект готов к работе."

# Проверяем наличие WireGuard
function check_wireguard_installed() {
  if [ -f "$WIREGUARD_BINARY" ]; then
    echo "True"
  else
    echo "False"
  fi
}

# Установка WireGuard
function install_wireguard() {
  if [ -f "$WIREGUARD_INSTALL_SCRIPT" ]; then
    echo "🔧 Запуск скрипта установки WireGuard..."
    bash "$WIREGUARD_INSTALL_SCRIPT"
  else
    echo "❌ Скрипт $WIREGUARD_INSTALL_SCRIPT не найден. Положите его в текущую директорию и повторите попытку."
  fi
}

# Удаление WireGuard
function remove_wireguard() {
  echo "❌ Удаление WireGuard..."
  yum remove wireguard -y 2>/dev/null || apt remove wireguard -y 2>/dev/null
}

# Меню для запуска
while true; do
  WIREGUARD_STATUS=$(check_wireguard_installed)
  echo "================== Меню =================="
  if [ "$WIREGUARD_STATUS" == "True" ]; then
    echo "✅ WireGuard установлен"
    echo "3. Переустановить WireGuard ♻️"
    echo "4. Удалить WireGuard 🗑️"
  else
    echo "3. Установить WireGuard ⚙️"
  fi
  echo "1. Запустить тесты"
  echo "2. Запустить основной скрипт (main.py)"
  echo "0. Выход"
  echo "=========================================="
  read -rp "Выберите действие: " choice
  case $choice in
    1)
      echo "🔍 Запуск тестов..."
      pytest "$PROJECT_DIR"
      ;;
    2)
      read -rp "Введите имя пользователя (nickname): " nickname
      python3 "$PROJECT_DIR/main.py" "$nickname"
      ;;
    3)
      if [ "$WIREGUARD_STATUS" == "True" ]; then
        install_wireguard
      else
        install_wireguard
      fi
      ;;
    4)
      if [ "$WIREGUARD_STATUS" == "True" ]; then
        remove_wireguard
      else
        echo "⚠️ WireGuard не установлен."
      fi
      ;;
    0)
      echo "👋 Выход. До свидания!"
      deactivate
      exit 0
      ;;
    *)
      echo "⚠️ Некорректный выбор. Попробуйте еще раз."
      ;;
  esac
done
