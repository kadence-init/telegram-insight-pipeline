"""
Главный управляющий модуль (оркестратор).

Запускает полный конвейер обработки данных:
1. Получает посты из Telegram (telegram_core).
2. Анализирует каждый пост с помощью AI (ai_core).
3. Визуализирует результаты в виде интерактивного дашборда (dashboard_core).
"""

import json
import asyncio

from telegram_core import get_posts_from_telegram
from ai_core import analyze_text
from dashboard_core import create_dashboard


def process_pipeline():
    """
    Основная функция, реализующая ETL-пайплайн (Extract, Transform, Load).
    """
    print(">>> Запуск информационного конвейера...")

    # ЭТАП 1: Extract - Извлечение данных из Telegram
    all_posts = asyncio.run(get_posts_from_telegram())
    if not all_posts:
        print("\n>>> Не удалось получить посты. Конвейер остановлен.")
        return []

    print(f"\n>>> Получено {len(all_posts)} постов для анализа. Начинаем обработку...")
    analysis_results = []

    # ЭТАП 2: Transform - Обработка каждого поста с помощью AI
    for post in all_posts:
        print(f"\n--- Анализируем пост ID {post['id']} из '{post['channel']}' ---")
        raw_analysis = analyze_text(post["text"])

        try:
            # Парсинг, проверка и обогащение данных
            analyzed_data = json.loads(raw_analysis)

            required_keys = ["summary", "sentiment", "topics"]
            if all(key in analyzed_data for key in required_keys):
                print("AI-анализ успешно получен и валидирован.")
                analyzed_data["source_id"] = post["id"]
                analyzed_data["source_channel"] = post["channel"]
                analysis_results.append(analyzed_data)
                print("AI-анализ успешно обработан.")
            else:
                print(
                    f"!!! Ошибка: AI вернул JSON без обязательных ключей: {raw_analysis}"
                )
        except (json.JSONDecodeError, TypeError):
            print(f"!!! Ошибка: AI вернул некорректный или пустой JSON: {raw_analysis}")

    print("\n>>> Обработка всех постов завершена.")
    return analysis_results


if __name__ == "__main__":
    # ЭТАП 3: Load/Present - Загрузка данных в дашборд для визуализации
    final_data = process_pipeline()

    if final_data:
        print("\n>>> Данные собраны. Запускаем дашборд...")
        create_dashboard(final_data)
    else:
        print("\n>>> Данные не были собраны. Дашборд не будет запущен.")
