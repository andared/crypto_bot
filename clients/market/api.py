import aiohttp

from settings import Settings
from yarl import URL


class MarketClient:
    def __init__(self) -> None:
        self.url = URL(Settings.MARKET_HOST)

    async def get_course_data(self, currency_id: str) -> dict:
        query_data = {
            "developer_data": "false",
            "community_data": "false",
            "tickers": "false",
            "localization": "false",
        }
        path = f"/api/v3/coins/{currency_id}"
        url = URL(Settings.MARKET_HOST).with_path(path).with_query(query_data).human_repr()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    return await resp.json()
        except Exception as e:
            return {"error": str(e)}


market_client = MarketClient()
