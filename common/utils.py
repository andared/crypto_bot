from common.constants import CURRENCY_TAGS


def remake_response(response: list[dict]):
    new_res = ""

    for obj in response:
        if not obj:
            continue
        new_res += f"\n{obj["tag"]} {CURRENCY_TAGS[obj["currency"]]}{obj["price"]}"

    return new_res
