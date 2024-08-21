import asyncio
import os
import datetime
from settings import logger
import json

from clients.tg import TgClient
from clients.redis import redis_client
from src.courses import get_all_cources, market_data_polling

from db.pg_client import pg_client
from db.pg_usage import get_data_pg, set_data_pg

from common.model import TABLE_USERS, TABLE_CRYPTOS


async def handle_callback_query(c: TgClient, callback_query):
    chat_id = callback_query['message']['chat']['id']
    try:
        data = json.loads(callback_query['data'])
    except json.JSONDecodeError:
        data = callback_query['data']

    if isinstance(data, dict):
        if data.get("system") == "subscription" and not data.get("period"):
            callback_data = lambda x: json.dumps({
                "system": "subscription",
                "name": data.get("name"),
                "period": x
            })
            keyboard = {
                'inline_keyboard': [
                    [{'text': '1 минута', 'callback_data': callback_data(60)}],
                    [{'text': '5 минут', 'callback_data': callback_data(300)}],
                    [{'text': '10 минут', 'callback_data': callback_data(600)}],
                    [{'text': '30 минут', 'callback_data': callback_data(1800)}],
                    [{'text': '60 минут', 'callback_data': callback_data(3600)}],
                    [{'text': 'Назад', 'callback_data': 'subscription'}],
                ]
            }
            await c.send_message(chat_id, f'Выберите частоту показа {data["name"]}', reply_markup=keyboard)
        elif data.get("system") == "subscription" and data.get("period"):
            await c.send_message(chat_id, f'Подписка активирована!\nКурс {data["name"]} каждые {int(data["period"] / 60)} минут')
    else:
        if data == "subscription":
            callback_data = lambda x: json.dumps({
                "system": "subscription",
                "name": x
            })
            keyboard = {
                'inline_keyboard': [
                    [
                        {'text': 'BTC', 'callback_data': callback_data('BTC')},
                        {'text': 'NOT', 'callback_data': callback_data('NOT')},
                        {'text': 'TON', 'callback_data': callback_data('TON')}
                    ]
                ]
            }
            await c.send_message(chat_id, 'Выберите криптовалюту, на которую хотите подписаться:', reply_markup=keyboard)
        else:
            await c.send_message(chat_id, f'You selected {data}')


async def run_echo():
    logger.info("Start TG polling")

    c = TgClient(os.getenv("BOT_TOKEN"))
    offset = 0
    watch_info = {}

    while True:
        watch_info = {}
        await __subscription_worker(c)

        tg_response = await c.get_updates_in_objects(offset=offset, timeout=60)

        if not tg_response:
            continue

        if not tg_response.get("result"):
            continue

        offset = tg_response.get("result")[-1].get("update_id") + 1

        users_data = get_data_pg()

        for item in reversed(tg_response.get("result")):
            if callback_query := item.get("callback_query"):
                await handle_callback_query(c, callback_query)
                continue

            chat_id = item["message"]["chat"]["id"]
            username = item["message"]["from"].get("username")

            for user in users_data:
                if user["chat_id"] == chat_id:
                    user_data = user

            last_message = item["message"]["text"]

            user_id = chat_id

            if watch_info.get(user_id):
                continue
            else:
                watch_info[user_id] = last_message

            logger.info(f"Get message '{last_message}' from '{username}'")

            set_data_pg([
                    {
                        "chat_id": chat_id,
                        "username": username,
                        "last_message": last_message,
                    }
                ])

            if "/usd" == last_message:
                set_data_pg([
                    {
                        "chat_id": chat_id,
                        "currency": "usd",
                    }
                ])
                await c.send_message(chat_id, 'Теперь курсы показываются в валюте usd')

            if "/eur" == last_message:
                set_data_pg([
                    {
                        "chat_id": chat_id,
                        "currency": "eur",
                    }
                ])
                await c.send_message(chat_id, 'Теперь курсы показываются в валюте eur')

            if "/rub" == last_message:
                set_data_pg([
                    {
                        "chat_id": chat_id,
                        "currency": "rub",
                    }
                ])
                await c.send_message(chat_id, 'Теперь курсы показываются в валюте rub')

            if "/courses" == last_message:
                try:
                    response = await get_all_cources(user_data["currency"])
                    if response:
                        await c.send_message(user_id, response)
                except Exception as e:
                    logger.error(f'Catch exception: {e}')

            if last_message == "/start" or last_message == "/info":
                await c.send_message(chat_id, 'Привет! Это бот с криптовалютами от @ryabokonnnn')

            if "/help" == last_message:
                await c.send_message(chat_id, 'Пожалуйста, напишите @ryabokonnnn')

            if "/stop" == last_message:
                set_data_pg([
                    {
                        "chat_id": chat_id,
                        "username": username,
                        "last_message": last_message,
                        "subscription_system": {
                            "enable": False
                        }
                    }
                ])
                await c.send_message(chat_id, 'Подписка деактивирована')

            if "/subscribe" in last_message:
                callback_data = lambda x: json.dumps({
                    "system": "subscription",
                    "name": x
                })
                keyboard = {
                    'inline_keyboard': [
                        [
                            {'text': 'BTC', 'callback_data': callback_data('BTC')},
                            {'text': 'NOT', 'callback_data': callback_data('NOT')},
                            {'text': 'TON', 'callback_data': callback_data('TON')}
                        ]
                    ]
                }
                await c.send_message(chat_id, 'Выберите криптовалюту, на которую хотите подписаться:', reply_markup=keyboard)

                data = {
                    "chat_id": chat_id,
                    "username": username,
                    "last_message": last_message,
                    "subscription_system": {
                        "enable": True,
                        "last_msg_ts": None,
                        "ts_range": None,
                    },
                }

                try:
                    data["subscription_system"]["ts_range"] = int(last_message.strip("/subscribe"))
                except Exception:
                    pass

                set_data_pg([data])


async def __subscription_worker(c: TgClient):
    users_data = get_data_pg()

    for user in users_data:
        if not user.get("subscription_system"):
            continue

        if not user["subscription_system"].get("enable"):
            continue

        if not user["subscription_system"].get("last_msg_ts"):
            await c.send_message(user["chat_id"], 'Подписка активирована')
            user["subscription_system"]["last_msg_ts"] = 1

        if not user["subscription_system"].get("ts_range"):
            user["subscription_system"]["ts_range"] = 300

        if (datetime.datetime.now().timestamp() - user["subscription_system"]["last_msg_ts"]) > user["subscription_system"]["ts_range"]:
            try:
                response = await get_all_cources(user["currency"])
                if response:
                    await c.send_message(user["chat_id"], response)
                    logger.info(f"Send message by subscription to {user['username']}")
            except Exception as e:
                logger.error(f'Catch exception: {e}')

            user["subscription_system"]["last_msg_ts"] = datetime.datetime.now().timestamp()

        set_data_pg([user])


async def main():
    pg_client.create_table(TABLE_USERS)
    pg_client.create_table(TABLE_CRYPTOS)
    await redis_client.connect()
    task2 = asyncio.create_task(market_data_polling())
    task1 = asyncio.create_task(run_echo())
    await asyncio.gather(task2, task1)


if __name__ == "__main__":
    try:
        logger.info(f'bot has been started {datetime.datetime.now()}')
        asyncio.run(main())
    except (KeyboardInterrupt):
        pass
    finally:
        pg_client.close()
        asyncio.run(redis_client.close())
        logger.info(f'\nbot has been stopped {datetime.datetime.now()}')
