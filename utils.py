from datetime import date
from datetime import datetime

from config import DAYS


# =========================================================
# МЕСЯЦЫ
# =========================================================

MONTHS = [

    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",

]


# =========================================================
# КЛЮЧ ТОРГОВОЙ ТОЧКИ
# =========================================================

def get_point_key(

    worker,
    weekday,
    route,
    shop,
    address,

):

    return (
        f"{worker}|"
        f"{weekday}|"
        f"{route}|"
        f"{shop}|"
        f"{address}"
    )


# =========================================================
# ДАТЫ ОПРЕДЕЛЁННОГО ДНЯ НЕДЕЛИ
# =========================================================

def get_dates_for_weekday(

    year,
    month,
    weekday,

):

    weekday_index = (
        DAYS.index(
            weekday
        )
    )


    dates = []

    current_date = date(
        year,
        month,
        1,
    )


    while current_date.month == month:


        if current_date.weekday() == weekday_index:

            dates.append(
                current_date
            )


        if current_date.day == 31:

            break


        try:

            current_date = date(

                current_date.year,

                current_date.month,

                current_date.day + 1,

            )


        except ValueError:

            break


    return dates


# =========================================================
# ДАТА ПО УМОЛЧАНИЮ
# =========================================================

def get_default_date(
    available_dates,
):

    today = date.today()


    # Если сегодня входит
    # в доступные даты

    if today in available_dates:

        return today


    # Берём ближайшую будущую дату

    future_dates = [

        value

        for value
        in available_dates

        if value >= today

    ]


    if future_dates:

        return future_dates[0]


    # Если будущих дат нет —
    # последняя доступная

    return available_dates[-1]


# =========================================================
# ФОРМАТИРОВАНИЕ ДАТЫ
# =========================================================

def format_date_short(
    value,
):

    months_short = [

        "янв",
        "фев",
        "мар",
        "апр",
        "мая",
        "июн",
        "июл",
        "авг",
        "сен",
        "окт",
        "ноя",
        "дек",

    ]


    return (
        f"{value.day:02d}."
        f"{months_short[value.month - 1]}"
    )
