import traceback
from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
from loguru import logger
import os
import random
import arrow
import pytz
from lunarcalendar import Converter, Solar, Lunar, DateNotExist


TZ = pytz.timezone("Asia/Shanghai")

TODAY = datetime.now()
START_DATE = os.environ["START_DATE"]
CITY = os.environ["CITY"]
BIRTHDAY: str = os.environ["BIRTHDAY"]

APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]

USER_ID = os.environ["USER_ID"]
TEMPLATE_ID = os.environ["TEMPLATE_ID"]
IS_LUNAR_BIRTHDAY: str = os.environ.get("IS_LUNAR_BIRTHDAY")


def get_weather(city: str):
    url = (
        "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city="
        + city
    )
    res: dict = requests.get(url).json()
    weather = res["data"]["list"][0]
    return weather["weather"], math.floor(weather["temp"])


def get_total_love_days(start_date: str) -> int:
    return (arrow.now(tz=TZ) - arrow.get(start_date, tzinfo=TZ)).days


def is_lunar_birthday(
    lunar_today: Lunar, birthday_month: str, birthday_day: str
) -> bool:
    if lunar_today.month == int(birthday_month) and lunar_today.day == int(
        birthday_day
    ):
        return True
    return False


def _get_lunar_today() -> Lunar:
    solar_today: arrow.Arrow = arrow.now(tz=TZ)
    logger.info(f"solar today, {solar_today=}")
    lunar_today: Lunar = Converter.Solar2Lunar(
        Solar(
            year=solar_today.date().year,
            month=solar_today.date().month,
            day=solar_today.date().day,
        )
    )

    logger.info(f"{lunar_today=}")
    return lunar_today


def _get_next_lunar_birthday(birthday: str) -> arrow.Arrow:
    """
    获取下一个农历生日
    :param birthday:
    :return:
    """
    logger.info(f"lunar {birthday=}")
    lunar_today: Lunar = _get_lunar_today()
    birthday_month, birthday_day = birthday.split("-")
    logger.info(f"{birthday_month=}, {birthday_day=}")
    next_lunar_birthday: Lunar = Lunar(
        year=lunar_today.year + 1, month=int(birthday_month), day=int(birthday_day)
    )
    logger.info(f"{next_lunar_birthday=}")
    return arrow.get(next_lunar_birthday.to_date(), tzinfo=TZ)


def _get_next_lunar_birthday_days_from_today(birthday: str) -> int:
    """
    获取下一个农历生日距离今天的天数
    :param birthday:
    :return:
    """
    lunar_today: Lunar = _get_lunar_today()
    birthday_month, birthday_day = birthday.split("-")

    # 今天是农历生日
    if is_lunar_birthday(
        lunar_today=lunar_today,
        birthday_month=birthday_month,
        birthday_day=birthday_day,
    ):
        logger.info("今天是农历生日")
        return 0
    next_lunar_birthday_arw: arrow.Arrow = _get_next_lunar_birthday(birthday)
    logger.info(f"{next_lunar_birthday_arw=}")
    days: int = (next_lunar_birthday_arw - arrow.now(tz=TZ)).days
    logger.info("next lunar birthday from today: {days=}")
    return days


def get_next_birthday_days_from_today(birthday: str, is_lunar: str = "") -> int:
    if is_lunar:
        return _get_next_lunar_birthday_days_from_today(birthday=birthday)
    next_birthday = datetime.strptime(
        f"{str(date.today().year)}-{birthday}", "%Y-%m-%d"
    )
    if next_birthday < datetime.now():
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    return (next_birthday - TODAY).days


def get_daily_sentence():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_daily_sentence()
    return words.json()["data"]["text"]


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_wx_msg_client(
    app_id: str,
    app_secret: str,
) -> WeChatMessage:
    client = WeChatClient(app_id, app_secret)
    return client.message


def send_wechat_message(
    client: WeChatMessage, user_id: str, template_id: str, data: dict
) -> dict:
    try:
        logger.info(f"send wechat message,{user_id=} {template_id=} {data=}")
        res: dict = client.send_template(
            user_id=user_id, template_id=template_id, data=data
        )
        logger.info(f"send wechat message success, {res=}")
        return res
    except Exception as e:
        logger.error(traceback.format_exc())
        return {}


def main():
    # client = WeChatClient(APP_ID, APP_SECRET)
    #
    # wm = WeChatMessage(client)
    wea, temperature = get_weather(city=CITY)
    data = {
        "weather": {"value": wea},
        "temperature": {"value": temperature},
        "love_days": {"value": get_total_love_days(START_DATE)},
        "birthday_left": {
            "value": get_next_birthday_days_from_today(
                birthday=BIRTHDAY, is_lunar=IS_LUNAR_BIRTHDAY
            )
        },
        "sentence": {"value": get_daily_sentence(), "color": get_random_color()},
    }
    logger.info(f"发送的消息体: {data=}")
    msg_client: WeChatMessage = get_wx_msg_client(app_id=APP_ID, app_secret=APP_SECRET)
    res: dict = send_wechat_message(
        client=msg_client, user_id=USER_ID, template_id=TEMPLATE_ID, data=data
    )
    logger.info(f"send template message resp, {res=}")


if __name__ == "__main__":
    main()
