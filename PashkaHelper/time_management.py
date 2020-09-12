import pytz
from datetime import datetime, time, date

ZERO_WEEK = date(2020, 9, 3).isocalendar()[1]

SERVER_TZ = pytz.timezone('UTC')
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


def get_weekday():
    return timezone_converter(datetime.utcnow(), SERVER_TZ, MOSCOW_TZ).weekday()


def timezone_converter(input_dt, current_dt, target_dt):
    return current_dt.localize(input_dt).astimezone(target_dt)


def get_week_parity():
    return 'even' if (datetime.today().isocalendar()[1] - ZERO_WEEK) % 2 != 0 else 'odd'


MORNING_MESSAGE_TIME = timezone_converter(
    datetime(
        year=2020,
        month=9,
        day=3,
        hour=23,
        minute=13
    ), MOSCOW_TZ, SERVER_TZ).time()
