import asyncio
import os
import sys
import logging
from loguru import logger
import subprocess
from concurrent.futures import ProcessPoolExecutor

def setup_logging():
    """Настройка логирования"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"  
    )
    
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/all_bots.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    
    logging.basicConfig(level=logging.INFO)

def run_bot(script_name, bot_name):
    """Запуск бота в отдельном процессе"""
    logger.info(f"Запуск {bot_name}...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка запуска {bot_name}: {e}")
    except KeyboardInterrupt:
        logger.info(f"{bot_name} остановлен")

async def main():
    """Основная функция запуска всех ботов"""
    setup_logging()
    
    logger.info("Запуск всех ботов автосервиса...")
    
    bots = [
        ("main.py", "Основной бот"),
        ("staff_bot.py", "Бот сотрудников"),
        ("service_bot.py", "Бот механиков СТО")
    ]
    
    try:
        with ProcessPoolExecutor(max_workers=len(bots)) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, run_bot, script, name)
                for script, name in bots
            ]
            
            await asyncio.gather(*tasks)
            
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения. Останавливаем ботов...")
    
    logger.info("Все боты остановлены")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
