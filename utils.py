import calendar

from datetime import date

# =========================================================

# МЕСЯЦЫ

# =========================================================

MONTHS = [

```
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
```

]

# =========================================================

# ДЕНЬ НЕДЕЛИ -> НОМЕР

# =========================================================

WEEKDAY_MAP = {

```
"Понедельник": 0,
"Вторник": 1,
"Среда": 2,
"Четверг": 3,
"Пятница": 4,
"Суббота": 5,
"Воскресенье": 6,
```

}

# =========================================================

# УНИКАЛЬНЫЙ КЛЮЧ ТТ

# =========================================================

def get_point_key(
worker,
weekday,
route,
shop,
address,
):

```
return (

    str(worker),

    str(weekday),

    str(route),

    str(shop),

    str(address),
)
```

# =========================================================

# ДАТЫ КОНКРЕТНОГО ДНЯ НЕДЕЛИ

# =========================================================

def get_dates_for_weekday(
year,
month,
weekday_name,
):

```
weekday_number = (
    WEEKDAY_MAP[
        weekday_name
    ]
)


days_in_month = (
    calendar.monthrange(
        year,
        month,
    )[1]
)


dates = []


for day_number in range(
    1,
    days_in_month + 1,
):

    current_date = date(
        year,
        month,
        day_number,
    )


    if (
        current_date.weekday()
        == weekday_number
    ):

        dates.append(
            current_date
        )


return dates
```

# =========================================================

# ДАТА ПО УМОЛЧАНИЮ

# =========================================================

def get_default_date(
available_dates,
):

```
today = date.today()


# Сегодня
if today in available_dates:

    return today


# Следующая доступная дата
future_dates = [

    value

    for value
    in available_dates

    if value >= today
]


if future_dates:

    return future_dates[0]


# Если месяц уже прошёл
return available_dates[-1]
```
