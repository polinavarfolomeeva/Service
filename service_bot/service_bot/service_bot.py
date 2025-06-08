import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from loguru import logger

from app.config.config import SERVICE_BOT_TOKEN, API_URL, BASE_URL
from app.handlers.service_handlers import service_router
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
        "logs/service_bot.log",
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

async def main():
    setup_logging()

    logger.info("Запуск бота для механиков СТО...")
    
    bot = Bot(token=SERVICE_BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(service_router)
    
    await setup_bot_commands(bot)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Бот механиков СТО запущен")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
