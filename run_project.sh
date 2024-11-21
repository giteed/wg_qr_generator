#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv" # Убедимся, что путь относительный, для создания в $PROJECT_DIR
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

echo -e "\n=== Установка проекта wg_qr_generator ==="

# Проверяем запуск с правами суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами суперпользователя (sudo)."
    echo "Например: sudo $0"
    exit 1
fi

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo "❌ Git не установлен. Установите его и повторите попытку."
  exit 1
fi

# Проверяем и при необходимости устанавливаем Node.js
if ! command -v node &>/dev/null; then
  echo "🔄 Node.js не установлен. Устанавливаю..."
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - || { echo "❌ Ошибка при добавлении репозитория Node.js."; exit 1; }
  sudo dnf install -y nodejs || { echo "❌ Ошибка при установке Node.js."; exit 1; }
  echo "✅ Node.js успешно установлен."
else
  echo "✅ Node.js уже установлен. Версия: $(node --version)"
fi

# Проверяем и восстанавливаем приоритет Python 3.11, если он сбит
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  sudo alternatives --set python3 $PYTHON_PATH || { echo "❌ Ошибка при настройке Python 3.11."; exit 1; }
  echo "✅ Python 3.11 настроен как основная версия."
else
  echo "❌ Python 3.11 не найден. Установите его вручную."
  exit 1
fi

# Проверяем наличие утилиты bc
install_bc_if_not_found() {
    if ! command -v bc &>/dev/null; then
        echo "🔄 Утилита 'bc' не найдена. Устанавливаю..."
        sudo dnf install -y bc || { echo "❌ Ошибка при установке утилиты 'bc'."; exit 1; }
        echo "✅ Утилита 'bc' успешно установлена."
    else
        echo "✅ Утилита 'bc' уже установлена."
    fi
}

install_bc_if_not_found

# Проверяем версию Python
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии $PYTHON_MAJOR.$PYTHON_MINOR обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO" || { echo "❌ Ошибка при клонировании репозитория."; exit 1; }
  FIRST_INSTALL=true
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull || { echo "❌ Ошибка при обновлении репозитория."; exit 1; }
  FIRST_INSTALL=false
fi

# Переходим в папку проекта
cd "$PROJECT_DIR" || exit

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR" || { echo "❌ Ошибка при создании виртуального окружения."; exit 1; }
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source "$VENV_DIR/bin/activate" || { echo "❌ Не удалось активировать виртуальное окружение."; exit 1; }

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
if [ "$FIRST_INSTALL" = true ]; then
  pip install --upgrade pip
  pip install -r "requirements.txt" || { echo "❌ Ошибка при установке зависимостей."; exit 1; }
else
  pip install --upgrade pip &>/dev/null
  pip install -r "requirements.txt" &>/dev/null
  echo "✅ Все зависимости уже установлены."
fi

# Проверяем наличие menu.py
if [ ! -f "menu.py" ]; then
  echo "❌ Файл menu.py не найден. Убедитесь, что он находится в папке $PROJECT_DIR."
  exit 1
fi

# Полезная информация перед запуском меню
echo -e "\n=== Полезная информация о системе ==="
echo "📌 Версия ОС: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo "📌 Версия ядра: $(uname -r)"
echo "📌 Внешний IP-адрес: $(curl -s ifconfig.me)"
echo "📌 Открытые порты в firewalld: $(sudo firewall-cmd --list-ports)"
echo "📌 Статус WireGuard: $(sudo systemctl is-active wg-quick@wg0)"
echo "📌 Ссылка на проект: https://github.com/licht8/wg_qr_generator"
echo "======================================"

# Выводим сообщение об успешной установке
echo "✅ Установка завершена. Проект готов к работе."

# Запускаем меню
echo -e "🔄 Запуск меню...\n"
python3 menu.py || { echo "❌ Ошибка при запуске меню."; exit 1; }
