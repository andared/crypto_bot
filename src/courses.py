import asyncio
from settings import logger
from clients.market.api import market_client
from clients.redis import redis_client

from common.constants import CryptoTags
from common.utils import remake_response


LAST_COURSES_DATA = {}


async def market_data_polling():
    logger.info("Start market polling")

    while True:
        for symbol in CryptoTags:
            crypto_data = await market_client.get_course_data(symbol.value)
            if crypto_data.get("market_data"):
                await redis_client.set_crypto(symbol.name, crypto_data)
            else:
                logger.warning("Catch bad response from daemon")
                await asyncio.sleep(60)

            await asyncio.sleep(15)


async def get_last_course(crypto_name: str, currency: str = "usd"):
    crypto_data = await redis_client.get_crypto(crypto_name)
    if not crypto_data:
        return {}
    return {
        "crypto": crypto_data["name"],
        "tag": crypto_data["symbol"].upper(),
        "currency": currency,
        "price": crypto_data["market_data"]["current_price"][currency],
        "time": crypto_data["last_updated"],
    }


async def get_all_cources(currency: str = "rub"):
    response = []

    for symbol in CryptoTags:
        crypto_data = await get_last_course(symbol.name, currency)
        response.append(crypto_data) if crypto_data else None

    for item in response:
        logger.info((item["tag"], item["price"], item["currency"], item["time"]))

    return remake_response(response)
