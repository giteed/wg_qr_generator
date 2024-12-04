#!/usr/bin/env python3

"""
swap_edit.py - Утилита для управления файлом подкачки (swap) в Linux

Особенности:
- Проверка и оптимизация swap.
- Поддержка параметров для гибкой настройки:
  * `--memory_required` или `--mr`: Назначает swap до 10% от объема диска.
  * `--min_swap` или `--ms`: Создает минимальный фиксированный swap (64 MB).
  * `--eco_swap`: Создает swap размером 2% от объема диска.
  * `--erase_swap`: Полностью удаляет swap.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from prettytable import PrettyTable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

from settings import PRINT_SPEED
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
    output = run_command("free -h")
    if not output:
        return None

    headers = ["Тип", "Общий", "Использовано", "Свободно"]
    rows = []
    for line in output.split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[0] in ("Mem:", "Swap:"):
            rows.append(parts[:4])

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
        disable_existing_swap(swap_file)

        display_message_slowly(f"   🛠️ Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        display_message_slowly("   🎨 Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        display_message_slowly("   ⚡ Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        display_message_slowly(f"   ✅ Swap создан. Размер: {size_mb} MB")
        if reason:
            display_message_slowly(f"   🔍 Запрошен {reason}")

    except Exception as e:
        display_message_slowly(f"   ❌ Произошла ошибка: {e}")


def swap_edit(size_mb=None, action=None):
    """Основная функция настройки swap."""
    check_root()

    display_message_slowly("📊 Состояние памяти:")
    swap_info = get_swap_info()
    if swap_info:
        print(swap_info)

    total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
    recommended_swap = min(total_disk // 10, 2048)  # 10% или максимум 2048 MB
    eco_swap = total_disk // 50  # 2% от диска
    min_swap = 64

    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    current_swap = int(current_swap) if current_swap else 0

    if action == "erase":
        disable_existing_swap()
        display_message_slowly("   ✅ Swap успешно удален.")
        return

    if action == "eco":
        size_mb = eco_swap
    elif action == "min":
        size_mb = min_swap
    elif size_mb:
        size_mb = min(size_mb, recommended_swap)

    if current_swap >= size_mb:
        display_message_slowly(
            f"✅ Текущий swap ({current_swap} MB) уже оптимален. Если хотите изменить, используйте --erase_swap."
        )
        return

    create_swap_file(size_mb, reason=action)

    # Показать итоговое состояние памяти
    display_message_slowly("📊 Итоговое состояние памяти:")
    final_swap_info = get_swap_info()
    if final_swap_info:
        print(final_swap_info)


if __name__ == "__main__":
    parser = ArgumentParser(description="Утилита для управления swap-файлом.")
    parser.add_argument("--memory_required", "--mr", type=int, help="Указать минимальный объем swap в MB.")
    parser.add_argument("--min_swap", "--ms", action="store_true", help="Создать минимальный swap (64 MB).")
    parser.add_argument("--eco_swap", action="store_true", help="Создать eco swap (2% от объема диска).")
    parser.add_argument("--erase_swap", action="store_true", help="Удалить swap.")
    args = parser.parse_args()

    if args.erase_swap:
        swap_edit(action="erase")
    elif args.eco_swap:
        swap_edit(action="eco")
    elif args.min_swap:
        swap_edit(action="min")
    elif args.memory_required:
        swap_edit(size_mb=args.memory_required, action="memory_required")
    else:
        swap_edit()

"""
### Полное описание скрипта `swap_edit.py`

**Назначение:**
Скрипт предназначен для управления и оптимизации файла подкачки (swap) в системах Linux. 
Его главная задача — обеспечить стабильность системы, особенно для серверов и приложений, критичных к использованию памяти. 
Правильная настройка swap помогает избежать сбоев из-за нехватки оперативной памяти.

---

#### Возможности:

1. **Проверка swap:**
   - Скрипт проверяет, существует ли файл подкачки в системе, и оценивает его текущий размер.

2. **Оптимизация swap:**
   - Если swap отсутствует, скрипт предлагает создать его с рекомендованным объемом (до 5% от общей файловой системы).
   - Если swap существует, но его размер меньше указанного в параметре `--memory_required` или меньше минимального рекомендованного, скрипт предлагает его расширить.

3. **Умный пропуск действий:**
   - Если swap уже оптимален, скрипт либо пропускает дальнейшие действия (в случае вызова из другого скрипта), либо уведомляет об этом (при запуске вручную).

4. **Расширенные режимы работы:**
   - Скрипт поддерживает интерактивное управление, а также автоматическую настройку через параметры командной строки.

---

#### Режимы работы:

1. **Интерактивный режим:**
   - Если скрипт запускается без аргументов, он предлагает пользователю выбрать размер swap, предоставляя подсказки и рекомендации.
   - Пример:
     ```bash
     sudo python3 swap_edit.py
     ```

2. **Режим с параметром `--memory_required`:**
   - Позволяет указать объем swap, необходимый для выполнения задачи, требовательной к памяти (до 10% от объема диска, не более 2048 MB).
   - Если текущий swap не удовлетворяет требованиям, скрипт предлагает увеличить его до заданного значения.
   - Пример:
     ```bash
     sudo python3 swap_edit.py --memory_required 1024
     ```

3. **Фиксированные режимы:**
   - `--min_swap` или `--ms`: Устанавливает фиксированный минимальный размер swap (64 MB).
   - `--eco_swap`: Устанавливает swap размером 2% от общего объема диска.
   - `--erase_swap`: Полностью удаляет swap.
   - Примеры:
     ```bash
     sudo python3 swap_edit.py --min_swap
     sudo python3 swap_edit.py --eco_swap
     sudo python3 swap_edit.py --erase_swap
     ```

4. **Вызов из других скриптов:**
   - Вы можете вызвать функцию `swap_edit` из другого скрипта для проверки и оптимизации swap.
   - Пример:
     ```python
     from modules.swap_edit import swap_edit

     # Проверить и установить swap размером 2048 MB
     swap_edit(size_mb=2048, action="memory_required")
     ```

---

#### Примеры работы:

1. **Swap отсутствует:**
   - Если swap отсутствует, скрипт выдает:
     ```
     ❌ Swap отсутствует в системе.
     Рекомендуется создать swap размером 512 MB (или введите свой размер).
     ```
   - Пользователь может согласиться с рекомендацией или указать другой размер.

2. **Недостаточный swap:**
   - Если текущий swap меньше минимального рекомендованного:
     ```
     🔍 Текущий swap: 256 MB. Рекомендуемый: 1024 MB.
     Хотите увеличить размер swap до 1024 MB? [Y/n]:
     ```
   - Пользователь может подтвердить или задать собственный размер.

3. **Swap уже оптимален:**
   - Если swap соответствует требованиям:
     - При вызове из другого скрипта:
       ```
       (действия пропускаются, сообщения не выводятся)
       ```
     - При запуске вручную:
       ```
       ✅ Текущий swap (2048 MB) уже оптимален.
       ```

4. **Удаление swap:**
   - При запуске с `--erase_swap`:
     ```
     🔍 Обнаружен существующий swap.
     🗑️ Swap удален успешно.
     ```

---

#### Зачем нужен swap?

1. **Резерв памяти:**
   Swap позволяет компенсировать нехватку оперативной памяти, выделяя место на диске для временного хранения данных.

2. **Стабильность системы:**
   Swap особенно важен для серверов, где нагрузка на память может неожиданно увеличиться.

3. **Гибкость настройки:**
   Swap можно оптимизировать под конкретные задачи, например, базы данных, рендеринг или анализ данных.

---

#### Итог:

Скрипт `swap_edit.py` — это мощный инструмент для настройки swap в Linux. 
Он подходит как для ручного управления, так и для интеграции в другие скрипты, помогая избежать проблем с нехваткой памяти 
и обеспечивая стабильную работу системы.
"""
