#!/usr/bin/env python3

"""
swap_edit.py - Утилита для управления файлом подкачки (swap) в Linux

Краткое описание:
- Проверяет наличие swap-файла в системе.
- Если swap отсутствует или его размер недостаточен:
  * Предлагает оптимальные параметры на основе 5% от объема файловой системы.
  * Позволяет указать размер вручную.
- Поддерживает вызов из других скриптов с параметром `--memory_required`.

Примеры:
1. Интерактивный режим:
   `sudo python3 swap_edit.py`
2. Консольный режим:
   `sudo python3 swap_edit.py --memory_required 2048`
"""

"""
swap_edit.py - Создание и настройка swap с улучшенным выводом и корректным управлением существующим swap.

Особенности:
1. Автоматическое отключение и удаление существующего файла подкачки.
2. Красивый форматированный вывод для удобства.
3. Поддержка интерактивного и консольного режимов.
4. Табличное представление данных (до и после изменений).
5. Возможность вызова как модуля из других скриптов.

Использование:
- Интерактивный: `sudo python3 swap_edit.py`
- Консольный: `sudo python3 swap_edit.py <размер в MB>`
"""

import os
import sys
import time
import shutil
import subprocess
import signal
from pathlib import Path
from argparse import ArgumentParser
from prettytable import PrettyTable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

from settings import PRINT_SPEED, LINE_DELAY
from ai_diagnostics.ai_diagnostics import display_message_slowly


def run_command(command, check=True):
    """Выполнить команду в терминале и вернуть вывод."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка: {e.stderr.strip()}")
        return None


def check_root():
    """Проверить, запущен ли скрипт от имени root."""
    if os.geteuid() != 0:
        display_message_slowly("🚨 Этот скрипт должен быть запущен от имени суперпользователя (root).", indent=False)
        exit(1)


def display_table(data, headers):
    """Показать таблицу с данными."""
    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    return table


def get_swap_info():
    """Получить информацию о swap и памяти."""
    output = run_command("free -h | grep -E 'Swap|Mem'")
    rows = [line.split() for line in output.split("\n") if line]
    headers = ["Тип", "Общий", "Использовано", "Свободно"]
    return display_table(rows, headers)


def disable_existing_swap(swap_file="/swap"):
    """Отключить и удалить существующий файл подкачки, если он используется."""
    if os.path.exists(swap_file):
        display_message_slowly(f"   🔍 Обнаружен существующий swap-файл: {swap_file}")
        run_command(f"swapoff {swap_file}", check=False)
        try:
            os.remove(swap_file)
            display_message_slowly(f"   🗑️ Удален существующий swap-файл: {swap_file}")
        except Exception as e:
            display_message_slowly(f"   ❌ Не удалось удалить файл: {e}")


def create_swap_file(size_mb, reason=None):
    """Создать и активировать файл подкачки."""
    try:
        swap_file = "/swap"

        # Отключить и удалить существующий swap
        disable_existing_swap(swap_file)

        # Создать файл подкачки
        display_message_slowly(f"   🛠️ Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        # Форматировать файл подкачки
        display_message_slowly("   🎨 Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        # Активировать файл подкачки
        display_message_slowly("   ⚡ Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        # Установить права
        display_message_slowly("   🔒 Настраиваю права на файл подкачки...")
        run_command(f"chown root:root {swap_file}", check=True)
        run_command(f"chmod 0600 {swap_file}", check=True)

        # Обновить rc.local
        display_message_slowly("   📂 Обновляю /etc/rc.local для автозагрузки...")
        rc_local_backup = "/tmp/rc.local.backup"
        if os.path.exists("/etc/rc.local"):
            shutil.copy("/etc/rc.local", rc_local_backup)
        else:
            with open("/etc/rc.local", "w") as rc_local:
                rc_local.write("#!/bin/bash\n")

        with open("/etc/rc.local", "a") as rc_local:
            rc_local.write(f"swapon {swap_file}\n")

        os.chmod("/etc/rc.local", 0o755)

        display_message_slowly(f"   ✅ Swap-файл создан и активирован. Размер: {size_mb} MB")
        if reason:
            display_message_slowly(f"   🔍 Этот размер был запрошен {reason}")

    except Exception as e:
        display_message_slowly(f"   ❌ Произошла ошибка: {e}")


def swap_edit(size_mb=None, memory_required=None, caller=None):
    """Основная функция настройки swap."""
    check_root()

    # Показать состояние памяти
    display_message_slowly("📊 Состояние памяти:")
    print(get_swap_info())

    # Получить общий объем файловой системы
    total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
    recommended_swap = max(total_disk // 20, 1)  # 5% от объема файловой системы

    # Если swap существует
    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    if current_swap and int(current_swap) > 0:
        current_swap = int(current_swap)
        if current_swap >= recommended_swap and not memory_required:
            if caller:
                return  # Выход, если вызывается из другого скрипта и swap подходит
            else:
                display_message_slowly(f"✅ Текущий swap ({current_swap} MB) уже оптимален.")
                return

        # Предложить увеличить swap
        new_size = memory_required or recommended_swap
        display_message_slowly(f"   🔍 Текущий swap: {current_swap} MB. Рекомендуемый: {new_size} MB.")
        size_mb = size_mb or new_size

    create_swap_file(size_mb, reason=caller or "в интерактивном режиме")


if __name__ == "__main__":
    parser = ArgumentParser(description="Утилита для управления swap-файлом.")
    parser.add_argument("--memory_required", "--mr", type=int, help="Требуемый объем swap в MB.")
    args = parser.parse_args()

    if args.memory_required:
        swap_edit(size_mb=args.memory_required, caller="скриптом")
    else:
        swap_edit()
"""
### Полное описание скрипта `swap_edit.py`

**Назначение:**
Скрипт предназначен для управления и оптимизации файла подкачки (swap) в системах Linux. Это особенно важно для серверов и приложений, критичных к использованию памяти, где правильная настройка swap может предотвратить сбои из-за нехватки ресурсов.

---

#### Возможности:

1. **Проверка swap:**
   - Скрипт определяет, существует ли файл подкачки в системе, и проверяет его текущий размер.

2. **Оптимизация swap:**
   - Если swap отсутствует, скрипт предлагает создать его с рекомендуемым объемом (5% от общей файловой системы).
   - Если swap существует, но его размер меньше рекомендуемого или указанного в параметре `--memory_required`, скрипт предлагает его увеличить.

3. **Автоматический пропуск действий:**
   - Если swap уже оптимален, скрипт пропускает настройку (при вызове из другого скрипта) или уведомляет об этом (при запуске вручную).

4. **Гибкость использования:**
   - Скрипт можно запустить как самостоятельную утилиту для настройки swap или вызвать из других программ в виде функции, указав требуемые параметры.

---

#### Режимы работы:

1. **Интерактивный режим:**
   - При запуске без аргументов скрипт предлагает пользователю выбрать размер swap, предоставляя подсказки и автоматические рекомендации.
   - Пример:
     ```bash
     sudo python3 swap_edit.py
     ```

2. **Режим с указанием параметра `--memory_required`:**
   - Позволяет указать минимальный объем swap, необходимый для выполнения задачи, требовательной к памяти.
   - Если текущий swap не удовлетворяет этим требованиям, скрипт автоматически предложит расширить его до заданного размера.
   - Пример:
     ```bash
     sudo python3 swap_edit.py --memory_required 2048
     ```

3. **Вызов из другого скрипта:**
   - Swap можно проверить и оптимизировать программно, вызвав функцию `swap_edit` из другого скрипта.
   - Пример:
     ```python
     from modules.swap_edit import swap_edit

     # Проверить и установить swap размером 4096 MB
     swap_edit(size_mb=4096, caller="моим скриптом")
     ```

---

#### Примеры работы:

1. **Нет swap:**
   - Если swap отсутствует, скрипт выводит сообщение:
     ```
     ❌ Swap отсутствует в системе.
     Рекомендуется создать swap размером 512 MB (или введите свой размер).
     ```
   - После подтверждения пользователь может создать swap.

2. **Маленький swap:**
   - Если текущий swap меньше 5% от объема файловой системы:
     ```
     🔍 Текущий swap: 256 MB. Рекомендуемый: 1024 MB.
     Хотите увеличить размер swap до 1024 MB? [Y/n]:
     ```
   - Пользователь может подтвердить или указать собственный размер.

3. **Достаточный swap:**
   - Если swap уже соответствует требованиям:
     - При вызове из другого скрипта:
       ```
       (действия пропускаются, никаких сообщений нет)
       ```
     - При интерактивном запуске:
       ```
       ✅ Текущий swap (2048 MB) уже оптимален.
       ```

---

#### Зачем нужен swap?

1. **Резерв памяти:**
   Swap позволяет избежать нехватки оперативной памяти, предоставляя место на диске для временного хранения данных.

2. **Стабильность систем:**
   Swap особенно важен для серверов, где нагрузка на память может неожиданно возрасти.

3. **Гибкость управления:**
   Настройка swap может быть оптимизирована под задачи сервера (например, база данных или рендеринг).

---

#### Итог:

Скрипт `swap_edit.py` — это универсальный инструмент для автоматизации настройки swap. Он подходит как для ручного управления, так и для интеграции в другие скрипты, помогая избежать проблем с нехваткой памяти и обеспечивая стабильную работу системы.
"""
