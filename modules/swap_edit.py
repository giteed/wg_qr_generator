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
Полное описание скрипта:
- Проверяет наличие swap и оптимизирует его параметры.
- Подходит для систем, критичных к использованию памяти.
- Поддерживает автоматический пропуск действий, если swap уже оптимален.
- Может вызываться из других скриптов с указанием необходимых параметров.
"""

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

