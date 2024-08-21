INFO = {
    "chat_id": {
        "username": str,
        "subscription_system": {
            "enable": bool,
            "crypto": str,
            "currency": str,
            "last_msg_ts": float | None,
            "ts_range": int | None,
        },
        "alarm_system": [
            {
                "enable": bool,
                "crypto": str,
                "currency": str,
                "period": int,
                "percentage": int | None,
                "threshold": float | None,
            }
        ]
    }
}

TABLE_USERS = "users"
TABLE_CRYPTOS = "cryptos"


ALARM_MODEL = {
    "enable": bool,
    "data": [
        {
            "name": str,
            "changes": [
                {
                    "period": int,
                    "percentage": int
                },
            ]
        }
    ]
}

ALARM_MODEL = {
    "enable": bool,
    "data": {
        f"crypto_name{str}": {
            f"period_{int}": int,
        },
    }
}

SUBSCRIPTION_MODEL = {
    "enable": bool,
    "data": {
        f"crypto_name{str}": {
            "period": int,
            "last_message_ts": float,
        },
    }
}
