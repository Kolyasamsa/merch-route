import calendar

from datetime import date

import pandas as pd
import streamlit as st

from auth import (
logout,
)

from database.visits import (
get_completed_visits_for_period,
)

from routes import (
get_workers,
)

from utils import (
MONTHS,
)

# =========================================================

# СТРАНИЦА СУПЕРВАЙЗЕРА

# =========================================================

def show_supervisor_dashboard(
df,
):

```
# =====================================================
# ЗАГОЛОВОК
# =====================================================

col_title, col_logout = (
    st.columns(
        [4, 1]
    )
)


with col_title:

    st.title(
        "📊 Табель мерчендайзеров"
    )


    st.caption(
        "Количество пройденных "
        "торговых точек"
    )


with col_logout:

    st.write("")

    if st.button(

        "🚪 Выйти",

        use_container_width=True,
    ):

        logout()


# =====================================================
# ВЫБОР МЕСЯЦА
# =====================================================

today = date.today()


col_year, col_month = (
    st.columns(2)
)


with col_year:


    year_options = [

        today.year - 1,

        today.year,

        today.year + 1,
    ]


    year = st.selectbox(

        "📅 Год",

        year_options,

        index=1,
    )


with col_month:


    month_name = (
        st.selectbox(

            "📅 Месяц",

            MONTHS,

            index=(
                today.month
                - 1
            ),
        )
    )


month = (
    MONTHS.index(
        month_name
    )
    \+ 1
)


# =====================================================
# ГРАНИЦЫ МЕСЯЦА
# =====================================================

days_in_month = (
    calendar.monthrange(

        year,

        month,
    )[1]
)


start_date = (
    date(

        year,

        month,

        1,
    )
    .isoformat()
)


end_date = (
    date(

        year,

        month,

        days_in_month,
    )
    .isoformat()
)


# =====================================================
# ЗАГРУЗКА ПРОХОЖДЕНИЙ
# =====================================================

try:

    visits = (
        get_completed_visits_for_period(

            start_date,

            end_date,
        )
    )


except Exception as error:

    st.error(
        f"Ошибка загрузки "
        f"табеля: {error}"
    )

    visits = []


# =====================================================
# ВСЕ МЕРЧЕНДАЙЗЕРЫ
# =====================================================

workers = (
    get_workers(
        df
    )
)


# =====================================================
# ВСЕ ДНИ МЕСЯЦА
# =====================================================

all_dates = [

    date(

        year,

        month,

        day_number,
    )

    for day_number
    in range(

        1,

        days_in_month
        \+ 1,
    )
]


date_columns = [

    current_date.strftime(
        "%d.%m"
    )

    for current_date
    in all_dates
]


# =====================================================
# СОЗДАЁМ ПУСТУЮ ТАБЛИЦУ
# =====================================================

table_data = []


for worker in workers:


    row = {

        "Мерчендайзер": worker
    }


    for column in date_columns:

        row[
            column
        ] = 0


    row[
        "Итого"
    ] = 0


    table_data.append(
        row
    )


table_df = (
    pd.DataFrame(
        table_data
    )
)


# =====================================================
# ЕСЛИ ЕСТЬ ПРОХОЖДЕНИЯ
# =====================================================

if visits:


    visits_df = (
        pd.DataFrame(
            visits
        )
    )


    visits_df[
        "visit_date"
    ] = (
        pd.to_datetime(

            visits_df[
                "visit_date"
            ]
        )
    )


    visits_df[
        "date_column"
    ] = (

        visits_df[
            "visit_date"
        ]
        .dt
        .strftime(
            "%d.%m"
        )
    )


    grouped = (

        visits_df

        .groupby(

            [
                "worker",

                "date_column",
            ]
        )

        .size()

        .reset_index(
            name="count"
        )
    )


    # =================================================
    # ЗАПОЛНЯЕМ ТАБЕЛЬ
    # =================================================

    for _, item in grouped.iterrows():


        worker = (
            item["worker"]
        )


        date_column = (
            item["date_column"]
        )


        count = (
            item["count"]
        )


        table_df.loc[

            table_df[
                "Мерчендайзер"
            ]
            == worker,

            date_column,

        ] = count


# =====================================================
# СЧИТАЕМ ИТОГО
# =====================================================

table_df[
    "Итого"
] = (

    table_df[
        date_columns
    ]
    .sum(
        axis=1
    )
)


# =====================================================
# ВЫВОД
# =====================================================

st.divider()


st.subheader(
    f"📅 Табель за "
    f"{month_name.lower()} "
    f"{year}"
)


st.dataframe(

    table_df,

    use_container_width=True,

    hide_index=True,
)


# =====================================================
# ОБЩАЯ СТАТИСТИКА
# =====================================================

st.divider()


total_visits = (
    int(
        table_df[
            "Итого"
        ].sum()
    )
)


st.metric(

    "Всего пройдено ТТ "
    "за месяц",

    total_visits,
)


# =====================================================
# СКАЧИВАНИЕ CSV
# =====================================================

csv_data = (
    table_df
    .to_csv(
        index=False
    )
    .encode(
        "utf-8-sig"
    )
)


st.download_button(

    "⬇️ Скачать табель CSV",

    data=csv_data,

    file_name=(

        f"табель_"

        f"{year}_"

        f"{month:02d}"

        f".csv"
    ),

    mime=(
        "text/csv"
    ),

    use_container_width=True,
)
```
