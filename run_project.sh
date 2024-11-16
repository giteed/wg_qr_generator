#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator
# Этот скрипт автоматически устанавливает проект, настраивает виртуальное окружение и предоставляет удобное меню для управления.

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv"

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

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
fi

# Клонируем или обновляем репозиторий
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

# Меню для запуска
while true; do
  echo "================== Меню =================="
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
