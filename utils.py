import calendar
from datetime import date


WEEKDAY_NUMBERS = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
}


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


def get_point_key(
    worker,
    day,
    route,
    shop,
    address,
):

    return "|".join(
        [
            str(worker),
            str(day),
            str(route),
            str(shop),
            str(address),
        ]
    )


def get_dates_for_weekday(
    year,
    month,
    weekday_name,
):

    weekday_number = (
        WEEKDAY_NUMBERS[weekday_name]
    )

    days_in_month = (
        calendar.monthrange(year, month)[1]
    )

    return [
        date(year, month, day_number)

        for day_number in range(
            1,
            days_in_month + 1,
        )

        if date(
            year,
            month,
            day_number,
        ).weekday() == weekday_number
    ]


def get_default_date(
    available_dates,
):

    today = date.today()

    if today in available_dates:
        return today

    future_dates = [
        item
        for item in available_dates
        if item >= today
    ]

    if future_dates:
        return future_dates[0]

    return available_dates[-1]
