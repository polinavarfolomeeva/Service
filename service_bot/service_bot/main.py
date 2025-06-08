import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from loguru import logger

from app.config.config import BOT_TOKEN, API_URL, BASE_URL
from app.handlers import main_router
from app.services.api_service import api_service

def setup_logging():

    logger.remove()

    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"  
    )

    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/bot.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )

    logging.basicConfig(level=logging.INFO)

async def setup_bot_commands(bot: Bot):

    commands = [
        BotCommand(command="start", description="Запустить бота / вернуться в главное меню"),
        BotCommand(command="help", description="Получить помощь по использованию бота"),
    ]

    await bot.set_my_commands(commands)

async def test_api():

    logger.info("Тестирование соединения с API...")
    logger.info(f"Используемый API URL: {API_URL}")
    logger.info(f"Базовый URL для запросов: {BASE_URL}")

    result = await api_service.test_connection()

    logger.info(f"Результат теста API: {result.get('status', 'Недоступен')}")

    logger.info("Тестирование запроса категорий...")
    categories_result = await api_service.get_categories()

    logger.info(f"Результат запроса категорий: {categories_result.get('status', 'Недоступен')}")

    if api_service.use_mock_data:
        logger.info("Бот настроен на использование тестовых данных для API запросов")
    else:
        logger.info("Бот настроен на использование реального API")

    return result

async def main():

    setup_logging()

    if not BOT_TOKEN:
        logger.error("Токен бота не найден в .env файле")
        return    
    try:
        await test_api()
    except Exception as e:
        logger.error(f"Ошибка при тестировании API: {e}")

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(main_router)

    await setup_bot_commands(bot)

    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:

        print("Запуск бота...")
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()
