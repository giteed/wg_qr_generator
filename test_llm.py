#!/usr/bin/env python3
# test_llm.py
# ==================================================
# Тестовый скрипт для проверки взаимодействия с LLM.
# Версия: 1.3 (2024-12-21)
# ==================================================
# Описание:
# Этот скрипт отправляет системный промпт и пользовательский промпт
# раздельно для проверки корректности работы модели.
# ==================================================

import requests
import logging

# Конфигурация API
LLM_API_URL = "http://10.67.67.2:11434/api/generate"
MODEL_NAME = "llama3:latest"

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def test_query_llm():
    """Тестовый запрос к LLM."""
    try:
        # Системный промпт
        system_prompt = "Вы профессиональный администратор WireGuard. Вас зовут Пулька. Начинайте каждый ответ с 'Привет, я Пулька!'"
        # Пользовательский промпт
        user_prompt = "Расскажите немного о себе."

        # Объединяем системный и пользовательский промпты
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }

        logger.info(f"Отправка запроса к LLM: {LLM_API_URL}")
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()

        result = response.json()
        logger.info(f"Ответ от LLM: {result.get('response', 'Ошибка: нет ответа')}")
        return result.get("response", "Ошибка: нет ответа")

    except requests.HTTPError as http_err:
        logger.error(f"HTTP ошибка при обращении к LLM: {http_err}")
        return f"HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    response = test_query_llm()
    print("Ответ LLM:")
    print(response)