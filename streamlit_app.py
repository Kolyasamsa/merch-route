import streamlit as st
import pandas as pd
from datetime import datetime
import os


# ==========================================
# НАСТРОЙКИ
# ==========================================

st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide"
)


EXCEL_FILE = "routes.xlsx"


# ==========================================
# ЗАГРУЗКА EXCEL
# ==========================================

@st.cache_data
def load_routes():

    if not os.path.exists(EXCEL_FILE):
        return None

    df = pd.read_excel(EXCEL_FILE)

    # Убираем лишние пробелы
    for column in [
        "Мерчендайзер",
        "Маршрут",
        "День",
        "Магазин",
        "Адрес"
    ]:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    return df


df = load_routes()


# ==========================================
# ПРОВЕРКА ФАЙЛА
# ==========================================

if df is None:

    st.error(
        "Файл routes.xlsx не найден. "
        "Загрузи его в GitHub рядом "
        "со streamlit_app.py"
    )

    st.stop()


# ==========================================
# ПРОВЕРКА СТОЛБЦОВ
# ==========================================

required_columns = [
    "Мерчендайзер",
    "Маршрут",
    "День",
    "Магазин",
    "Адрес"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "В Excel отсутствуют столбцы: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ==========================================
# ДНИ НЕДЕЛИ
# ==========================================

days = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]


# ==========================================
# ОПРЕДЕЛЯЕМ СЕГОДНЯ
# ==========================================

weekday_number = datetime.today().weekday()

if weekday_number < 5:

    today = days[weekday_number]

else:

    today = "Понедельник"


# ==========================================
# ЗАГОЛОВОК
# ==========================================

st.title("📍 Маршруты мерчендайзеров")

st.caption(
    "Контроль торговых точек и прохождения маршрутов"
)


# ==========================================
# ВЫБОР МЕРЧЕНДАЙЗЕРА
# ==========================================

workers = sorted(
    df["Мерчендайзер"]
    .unique()
    .tolist()
)


worker = st.selectbox(
    "👤 Мерчендайзер",
    workers
)


# ==========================================
# ВЫБОР ДНЯ
# ==========================================

available_days = [
    day
    for day in days
    if day in df[
        df["Мерчендайзер"] == worker
    ]["День"].unique()
]


if today in available_days:

    default_day_index = (
        available_days.index(today)
    )

else:

    default_day_index = 0


day = st.selectbox(
    "📅 День",
    available_days,
    index=default_day_index
)


# ==========================================
# ФИЛЬТРУЕМ МАРШРУТЫ
# ==========================================

day_data = df[
    (df["Мерчендайзер"] == worker)
    &
    (df["День"] == day)
]


routes = sorted(
    day_data["Маршрут"]
    .unique()
    .tolist()
)


st.divider()


# ==========================================
# ИНФОРМАЦИЯ
# ==========================================

st.subheader(
    f"👤 {worker}"
)

st.write(
    f"📅 **{day}**"
)

st.write(
    f"Маршрутов на сегодня: "
    f"**{len(routes)}**"
)

st.write(
    f"Всего ТТ: "
    f"**{len(day_data)}**"
)


# ==========================================
# ВЫВОД МАРШРУТОВ
# ==========================================

for route in routes:

    route_data = day_data[
        day_data["Маршрут"] == route
    ]

    st.divider()

    st.subheader(
        f"🚗 {route}"
    )

    st.write(
        f"Торговых точек: "
        f"**{len(route_data)}**"
    )


    # ======================================
    # ТОРГОВЫЕ ТОЧКИ
    # ======================================

    for number, (
        index,
        point
    ) in enumerate(
        route_data.iterrows(),
        start=1
    ):

        with st.expander(

            f"🔴 {number}. "
            f"{point['Магазин']} — "
            f"{point['Адрес']}",

            expanded=False

        ):

            st.write(
                f"🏪 **Магазин:** "
                f"{point['Магазин']}"
            )

            st.write(
                f"📍 **Адрес:** "
                f"{point['Адрес']}"
            )


# ==========================================
# ТЕХНИЧЕСКАЯ ПРОВЕРКА
# ==========================================

with st.expander(
    "🔧 Проверка данных"
):

    st.write(
        f"Всего мерчендайзеров: "
        f"{len(workers)}"
    )

    for worker_name in workers:

        worker_data = df[
            df["Мерчендайзер"]
            == worker_name
        ]

        st.write(
            f"**{worker_name}: "
            f"{len(worker_data)} ТТ**"
        )
