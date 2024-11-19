#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="$PROJECT_DIR/venv"
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

echo "=== Установка проекта wg_qr_generator ==="

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo "❌ Git не установлен. Установите его и повторите попытку."
  exit 1
fi

# Установка Node.js
echo "🔄 Установка Node.js..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs
if command -v node &>/dev/null; then
  echo "✅ Node.js установлен. Версия: $(node --version)"
else
  echo "❌ Ошибка при установке Node.js."
 exit 1
fi

# Проверяем и восстанавливаем приоритет Python 3.11, если он сбит
echo --- 
python3 --version 
echo ---
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  # Устанавливаем Python 3.11 как основную версию
  sudo alternatives --set python3 $PYTHON_PATH
  echo "✅ Python 3.11 настроен как основная версия."
else
  echo "❌ Python 3.11 не найден. Установите его вручную."
  exit 1
fi


install_bc_if_not_found() {
    if ! command -v bc &> /dev/null; then
        echo "Утилита 'bc' не найдена. Устанавливаю..."
        sudo dnf install bc -y
    else
        echo "Утилита 'bc' уже установлена."
    fi
}

install_bc_if_not_found

# Проверяем версию Python
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.major, sys.version_info.minor)')
if [[ "$PYTHON_VERSION" < "3 8" ]]; then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии 3.$(echo $PYTHON_VERSION | awk '{print $2}') обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO"
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull
fi

# Переходим в папку проекта
cd "$PROJECT_DIR" || exit

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR"
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source "$VENV_DIR/bin/activate" || { echo "❌ Не удалось активировать виртуальное окружение."; exit 1; }

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r "requirements.txt"
else
  echo "⚠️ Файл requirements.txt не найден. Проверьте проект."
fi

# Проверяем наличие menu.py
if [ ! -f "menu.py" ]; then
  echo "❌ Файл menu.py не найден. Убедитесь, что он находится в папке $PROJECT_DIR."
  exit 1
fi

# Выводим сообщение об успешной установке
echo "✅ Установка завершена. Проект готов к работе."

# Запускаем меню
echo "🔄 Запуск меню..."
python3 menu.py || { echo "❌ Ошибка при запуске меню."; exit 1; }
