#!/bin/bash
# run_project.sh
## Установочный скрипт для проекта wg_qr_generator
# Этот скрипт устанавливает проект, создаёт виртуальное окружение и запускает меню.

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

# Проверяем версию Python3
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info >= (3, 8))')
if [ "$PYTHON_VERSION" != "True" ]; then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии 3.8 или выше обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO" "$PROJECT_DIR"
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull
fi

# Переходим в директорию проекта
cd "$PROJECT_DIR" || exit

# Создаем виртуальное окружение внутри папки проекта
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR"
fi

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate"

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r "requirements.txt"
else
  echo "⚠️ Файл requirements.txt не найден. Проверьте проект."
fi

echo "✅ Установка завершена. Проект готов к работе."

# Запускаем меню
python3 menu.py
