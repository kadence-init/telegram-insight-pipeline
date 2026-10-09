"""
Модуль для обработки данных (Transform).
Отвечает за взаимодействие с GigaChat API для анализа текста,
включая автоматическое управление жизненным циклом Access Token.
"""

import os
import json
import requests
import urllib3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Отключаем предупреждения о небезопасном соединении (self-signed certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загрузка конфигурации из .env файла
load_dotenv()
GIGACHAT_API_KEY = os.environ.get("GIGACHAT_API_KEY")

# Глобальные переменные для кэширования Access Token в рамках одного сеанса
access_token = None
token_expires_at = None


def _get_or_refresh_token():
    """
    Внутренняя функция для получения или обновления Access Token (OAuth 2.0).
    Токен запрашивается только в случае его отсутствия или истечения срока действия.
    """
    global access_token, token_expires_at

    # Используем закэшированный токен, если он валиден
    if access_token and datetime.now() < token_expires_at - timedelta(minutes=1):
        return

    print("--- Модуль AI: Обновление Access Token... ---")
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",
        "Authorization": f"Basic {GIGACHAT_API_KEY}",
    }
    payload = "scope=GIGACHAT_API_PERS"

    try:
        response = requests.post(
            url, headers=headers, data=payload, verify=False, timeout=10
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in_ms = token_data["expires_at"]
        token_expires_at = datetime.now() + timedelta(milliseconds=expires_in_ms)
        print(">>> Access Token успешно обновлен.")
    except requests.exceptions.RequestException as e:
        print(f"!!! Ошибка при получении Access Token: {e}")
        access_token = None


def analyze_text(text_to_analyze: str) -> str:
    """
    Отправляет текст на анализ в GigaChat API и возвращает результат в виде JSON-строки.

    Args:
        text_to_analyze: Текст новостного поста для анализа.

    Returns:
        JSON-строка с результатами анализа или сообщением об ошибке.
    """
    _get_or_refresh_token()
    if not access_token:
        return '{"error": "Не удалось получить Access Token для GigaChat"}'

    # Системный промпт, спроектированный для получения строгого JSON-ответа
    # с классификацией по заданным категориям.
    prompt = f"""
    ### ЗАДАЧА ###
    Проанализируй новостной пост. Верни ответ ТОЛЬКО в формате JSON.

    ### ИНСТРУКЦИИ ПО ПОЛЯМ ###
    1.  "summary" (Сводка): Краткая сводка поста в 1-2 предложениях. СТИЛЬ: Строго безличный, новостной, фактологический. НЕ ИСПОЛЬЗУЙ вводные фразы вроде "В посте говорится о...".
    2.  "sentiment" (Тональность): Определи общую тональность. ЗНАЧЕНИЯ: Только "Positive", "Negative" или "Neutral".
    3.  "topics" (Категории): Выбери 2-3 наиболее подходящие категории из СТРОГО ОПРЕДЕЛЕННОГО СПИСКА. СПИСОК: ["AI", "Технологии", "Гаджеты", "Бизнес", "Финансы", "Политика", "Наука", "Общество", "Криптовалюты", "Общее"].

    ### ТЕКСТ ПОСТА ДЛЯ АНАЛИЗА ###
    ---
    {text_to_analyze}
    ---
    """

    url = "https://api.giga.chat/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "GigaChat-2-Pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 512,
    }

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload), verify=False, timeout=20
        )
        response.raise_for_status()
        result = response.json()
        # Извлечение полезной нагрузки из сложной структуры ответа API
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f'{{"error": "Ошибка при запросе к GigaChat API", "details": "{e}"}}'


if __name__ == "__main__":
    # Блок для автономной проверки работоспособности модуля
    print("--- ЗАПУСК ai_core.py В РЕЖИМЕ ПРОВЕРКИ ---")
    example_text = "Apple анонсировала новый MacBook Pro с чипом M4. Аналитики прогнозируют рекордные продажи."
    analysis_result = analyze_text(example_text)
    print("\n--- РЕЗУЛЬТАТ АНАЛИЗА ---")
    print(analysis_result)
