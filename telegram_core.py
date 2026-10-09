"""
Модуль для сбора данных (Extract).
Отвечает за асинхронное взаимодействие с Telegram API для получения
постов из указанных публичных каналов.
"""

import os
import asyncio
from telethon.sync import TelegramClient
from dotenv import load_dotenv

# Загрузка конфигурации из .env файла
load_dotenv()
API_ID = os.environ.get("TELEGRAM_API_ID")
API_HASH = os.environ.get("TELEGRAM_API_HASH")

# Имя файла для сохранения сессии, чтобы избежать повторной авторизации
SESSION_NAME = "telegram_session"

# Список публичных Telegram-каналов для анализа
TARGET_CHANNELS = [
    "forbesrussia",
    "durov_russia",
    "exploitex",
    "postnauka",
    "arzamaslive",
]


async def get_posts_from_telegram(post_limit_per_channel: int = 3):
    """
    Асинхронно подключается к Telegram и получает N последних постов
    из каждого канала в списке TARGET_CHANNELS.

    Args:
        post_limit_per_channel: Количество постов для сбора из каждого канала.

    Returns:
        Список словарей, где каждый словарь представляет собой пост.
    """
    print("--- Модуль Telegram: Инициализация ---")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    all_posts = []

    try:
        await client.start()
        print(">>> Успешное подключение к Telegram.")

        for channel in TARGET_CHANNELS:
            print(f"--- Сбор данных из канала: {channel} ---")
            # Асинхронный итератор для эффективной работы с сетью
            async for message in client.iter_messages(
                channel, limit=post_limit_per_channel
            ):
                if message.text:
                    all_posts.append(
                        {
                            "id": message.id,
                            "channel": channel,
                            "text": message.text,
                        }
                    )

    except Exception as e:
        print(f"!!! Ошибка при работе с Telegram API: {e}")
    finally:
        await client.disconnect()
        print(">>> Отключение от Telegram.")

    return all_posts


if __name__ == "__main__":
    # Блок для автономной проверки работоспособности модуля
    print("--- ЗАПУСК telegram_core.py В РЕЖИМЕ ПРОВЕРКИ ---")
    results = asyncio.run(get_posts_from_telegram())

    if results:
        print(f"\n✅ Успешно получено {len(results)} постов.")
        for post in results:
            print(f"  - Канал: '{post['channel']}', Текст: '{post['text'][:70]}...'")
    else:
        print("\n❌ Посты не были получены.")
