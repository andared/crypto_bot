import json

from db.pg_client import pg_client
from common.model import TABLE_USERS


def get_data_pg():
    response = []
    data = pg_client.select_from_table(TABLE_USERS)

    for user_data in data:
        chat_id, username, subscription_system, alarm_system, last_message, currency = user_data
        response.append(
            {
                "chat_id": chat_id,
                "username": username,
                "last_message": last_message,
                "currency": currency or "usd",
                "subscription_system": subscription_system,
                "alarm_system": alarm_system,
            }
        )

    return response


def set_data_pg(data: list[dict]):
    for item in data:
        pg_client.insert_into_table(
            TABLE_USERS,
            item["chat_id"],
            item["username"] if item.get("username") else None,
            item["last_message"] if item.get("last_message") else None,
            json.dumps(item["subscription_system"]) if item.get("subscription_system") else None,
            json.dumps(item["alarm_system"]) if item.get("alarm_system") else None,
            item["currency"] if item.get("currency") else None,
        )

    return True
