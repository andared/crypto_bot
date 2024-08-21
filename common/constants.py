from enum import Enum


class CryptoTags(Enum):
    NOT = "notcoin"
    TON = "the-open-network"
    BTC = "bitcoin"


CURRENCY_TAGS = {
    "usd": "$",
    "rub": "₽",
    "eur": "€"
}

FAKE_DATA = {
    234103859: {
        "subscription_system": {
            "enable": True,
            "last_msg_ts": 1718500513.25577,
            "ts_range": 3600
        },
        "alarm_system": {
            "enable": False,
        },
        "username": "ryabokonnnn",
    }
}
