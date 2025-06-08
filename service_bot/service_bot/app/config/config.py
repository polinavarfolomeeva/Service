import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
STAFF_BOT_TOKEN = os.getenv("STAFF_BOT_TOKEN")
SERVICE_BOT_TOKEN = os.getenv("SERVICE_BOT_TOKEN")

API_URL = os.getenv("API_URL")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

BASE_URL = API_URL
if BASE_URL and "/test" in BASE_URL:

    if BASE_URL.endswith("/api"):
        BASE_URL = BASE_URL[:-4]  

logger.debug(f"API_URL from config: {API_URL}")
logger.debug(f"BASE_URL for API requests: {BASE_URL}")
