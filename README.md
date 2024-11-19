# wg_qr_generator

**wg_qr_generator** – это система автоматизации управления WireGuard, включающая генерацию конфигураций, создание QR-кодов, управление пользователями и очистку устаревших данных.

Система включает веб-интерфейс на базе **Gradio** для удобного управления пользователями и конфигурациями через браузер.

---

## Основные возможности

- **Генерация конфигураций**: Автоматическое создание конфигурационных файлов и QR-кодов для пользователей.
- **Управление сроком действия**: Проверка, продление, сброс срока действия аккаунтов.
- **Удаление устаревших данных**: Автоматическое удаление просроченных аккаунтов, IP-адресов и QR-кодов.
- **Синхронизация конфигураций**: Интеграция с сервером WireGuard.
- **Веб-интерфейс**: Простая и удобная админка на базе Gradio для управления пользователями.

---

## Веб-интерфейс Gradio

**Gradio Admin Panel** предоставляет интерфейс для:

- Просмотра списка пользователей.
- Создания нового пользователя.
- Ручного удаления пользователей.
- Просмотра состояния системы и текущих конфигураций.

### Как запустить админку

После установки проекта из меню выберите пункт:

```plaintext
3. Открыть админку
```

Админка запускается на порту **7860**, по умолчанию доступна по локальному адресу:

```
http://127.0.0.1:7860
```

Если сервер имеет внешний IP, вы можете открыть админку в интернете. Для этого включите публичный доступ на порт **7860** через `firewalld`. Скрипт настройки проекта автоматически откроет этот порт.

Админка также предоставляет временные публичные ссылки через Gradio:

```
🌐 Публичная ссылка: https://<уникальный_адрес>.gradio.live
```

---

## Требования

Перед установкой убедитесь, что в системе установлены:
1. **Python 3.8+** (рекомендуется Python 3.11).
2. **Git** для клонирования репозитория.
3. **Node.js** для работы Gradio (устанавливается автоматически).

### Установка Python, Git и Node.js на CentOS Stream 8

Для установки выполните команду:

```bash
sudo dnf update -y && sudo dnf install epel-release -y && curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && sudo dnf install -y nodejs && node --version  && sudo dnf update -y && sudo dnf install git mc tar gcc curl openssl-devel bzip2-devel libffi-devel zlib-devel -y && sudo dnf install net-tools -y && sudo dnf install python3.11 -y && sudo alternatives --set python3 /usr/bin/python3.11 && python3 --version
```

Эта команда:
- Обновляет систему.
- Устанавливает необходимые зависимости.
- Устанавливает Python 3.11, Git и Node.js.

---

## Установка и запуск проекта

### Быстрая установка

Для установки, настройки и запуска проекта выполните следующую команду:
```bash
mkdir -p pyWGgen && cd pyWGgen && wget https://raw.githubusercontent.com/licht8/wg_qr_generator/refs/heads/main/run_project.sh && chmod +x run_project.sh && ./run_project.sh
```

### Что делает эта команда:
1. Создает директорию `pyWGgen` и переходит в нее.
2. Скачивает скрипт `run_project.sh` из репозитория.
3. Делает скрипт `run_project.sh` исполняемым.
4. Запускает скрипт, который:
   - Проверяет наличие Python, Git и Node.js.
   - Создает виртуальное окружение и устанавливает зависимости.
   - Открывает меню для работы с проектом.

---

## Использование меню

После запуска `run_project.sh` вы получите удобное меню:

1. **Запустить тесты**: Проверяет основные модули проекта.
2. **Запустить основной скрипт (main.py)**: Генерация конфигураций для пользователей.
3. **Открыть админку**: Запуск веб-интерфейса на Gradio.
4. **Переустановить WireGuard**: Устанавливает WireGuard с помощью `wireguard-install.sh`.
5. **Удалить WireGuard**: Полностью удаляет WireGuard с сервера.
0. **Выход**: Завершает работу программы.

---

## Структура проекта

```plaintext
wg_qr_generator-main
├── LICENSE
├── README.md
├── cleanup.py
├── main.py
├── manage_expiry.py
├── menu.py
├── requirements.txt
├── run_project.sh
├── settings.py
├── wireguard-install.sh
├── gradio_admin
│   ├── __init__.py
│   ├── create_user.py
│   ├── delete_user.py
│   ├── list_users.py
│   ├── main_interface.py
│   ├── search_user.py
├── modules
│   ├── account_expiry.py
│   ├── check_user.py
│   ├── client_config.py
│   ├── config.py
│   ├── config_writer.py
│   ├── directory_setup.py
│   ├── ip_management.py
│   ├── keygen.py
│   ├── qr_generator.py
│   ├── sync.py
│   ├── user_management.py
│   ├── utils.py
└── test
    ├── test_account_expiry.py
    ├── test_check_user.py
    ├── test_config_writer.py
    ├── test_directory_setup.py
    ├── test_ip_management.py
    ├── test_keygen.py
    ├── test_qr_generator.py
    ├── test_sync.py
    └── test_user_management.py
```

---

## Тестирование

Запуск тестов через меню или командой:
```bash
pytest
```

---

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).

---

## Контакты

Если у вас есть вопросы или предложения, свяжитесь с нами через [Issues](https://github.com/licht8/wg_qr_generator/issues).
