from environs import Env
from dotenv import load_dotenv
import logging

formatter = logging.Formatter('%(asctime)s: [%(funcName)s] [%(levelname)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

load_dotenv()
env = Env()


class Settings:
    BOT_TOKEN = env.str("BOT_TOKEN")
    ADMIN_ID = env.int("ADMIN_ID")
    WEBHOOK_TOKEN = env.str("WEBHOOK_TOKEN")
    ADMIN_PASSWORD = env.str("ADMIN_PASSWORD")
    IS_PRODUCTION = env.bool("IS_PRODUCTION", False)
    LOG_BOT_TOKEN = env.str("LOG_BOT_TOKEN", "")
    HOST = env.str("HOST", "")
    PORT = env.int("PORT", "")
    MARKET_HOST = env.str("COINGECKO_HOST", "")

    POSTGRES_DB = env.str("POSTGRES_DB", "")
    POSTGRES_USER = env.str("POSTGRES_USER", "")
    POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", "")
