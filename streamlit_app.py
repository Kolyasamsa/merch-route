import streamlit as st
import pandas as pd
from datetime import datetime, date
import os


# =========================================================
# НАСТРОЙКИ СТРАНИЦЫ
# =========================================================

st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide"
)


# =========================================================
# НАСТРОЙКИ
# =========================================================

EXCEL_FILE = "routes.xlsx"

DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]


# =========================================================
# СОСТОЯНИЕ ПРИЛОЖЕНИЯ
# =========================================================

if "completed_points" not in st.session_state:
    st.session_state.completed_points = {}

if "point_comments" not in st.session_state:
    st.session_state.point_comments = {}

if "point_photos" not in st.session_state:
    st.session_state.point_photos = {}

if "completion_times" not in st.session_state:
    st.session_state.completion_times = {}


# =========================================================
# ЗАГРУЗКА МАРШРУТОВ ИЗ EXCEL
# =========================================================

@st.cache_data
def load_routes():

    if not os.path.exists(EXCEL_FILE):
        return None

    df = pd.read_excel(EXCEL_FILE)

    required_columns = [
        "Мерчендайзер",
        "Маршрут",
        "День",
        "Магазин",
        "Адрес"
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"В Excel нет столбца: {column}"
            )

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Убираем полностью пустые строки
    df = df[
        df["Мерчендайзер"] != ""
    ]

    return df


# =========================================================
# ЗАГРУЖАЕМ EXCEL
# =========================================================

try:

    df = load_routes()

except Exception as e:

    st.error(
        f"Ошибка при чтении Excel: {e}"
    )

    st.stop()


if df is None:

    st.error(
        f"Файл {EXCEL_FILE} не найден."
    )

    st.stop()


# =========================================================
# ОПРЕДЕЛЯЕМ ТЕКУЩИЙ ДЕНЬ
# =========================================================

weekday_number = datetime.today().weekday()

if weekday_number < 5:

    today_day = DAYS[weekday_number]

else:

    today_day = "Понедельник"


# =========================================================
# ЗАГОЛОВОК
# =========================================================

st.title("📍 Маршруты мерчендайзеров")

st.caption(
    "Контроль прохождения торговых точек"
)


# =========================================================
# ВЫБОР МЕРЧЕНДАЙЗЕРА
# =========================================================

workers = sorted(
    df["Мерчендайзер"]
    .dropna()
    .unique()
    .tolist()
)


worker = st.selectbox(
    "👤 Мерчендайзер",
    workers
)


# =========================================================
# ДОСТУПНЫЕ ДНИ ДЛЯ ЭТОГО МЕРЧЕНДАЙЗЕРА
# =========================================================

worker_data = df[
    df["Мерчендайзер"] == worker
]


available_days = [
    day
    for day in DAYS
    if day in worker_data["День"].unique()
]


if today_day in available_days:

    default_day_index = available_days.index(
        today_day
    )

else:

    default_day_index = 0


day = st.selectbox(
    "📅 День маршрута",
    available_days,
    index=default_day_index
)


# =========================================================
# ДАТА ПРОХОЖДЕНИЯ
#
# Она нужна, чтобы каждый новый вторник
# создавал отдельный отчёт.
# =========================================================

selected_date = st.date_input(
    "📅 Дата прохождения",
    value=date.today(),
    format="DD.MM.YYYY"
)


date_key = selected_date.strftime(
    "%Y-%m-%d"
)


# =========================================================
# ФИЛЬТРУЕМ ТЕКУЩИЙ ДЕНЬ
# =========================================================

day_data = worker_data[
    worker_data["День"] == day
].copy()


routes = (
    day_data["Маршрут"]
    .dropna()
    .unique()
    .tolist()
)


# =========================================================
# ИНФОРМАЦИЯ О МАРШРУТЕ
# =========================================================

st.divider()

st.subheader(
    f"👤 {worker}"
)

st.write(
    f"📅 **{day}, "
    f"{selected_date.strftime('%d.%m.%Y')}**"
)

st.write(
    f"Маршрутов: **{len(routes)}**"
)

st.write(
    f"Всего ТТ: **{len(day_data)}**"
)


# =========================================================
# СОЗДАНИЕ УНИКАЛЬНОГО ID ТТ
# =========================================================

def get_point_id(point):

    return (
        f"{date_key}|"
        f"{worker}|"
        f"{day}|"
        f"{point['Маршрут']}|"
        f"{point['Магазин']}|"
        f"{point['Адрес']}"
    )


# =========================================================
# ВЫВОД МАРШРУТОВ
# =========================================================

for route in routes:

    route_data = day_data[
        day_data["Маршрут"] == route
    ]

    total_points = len(route_data)

    completed_count = 0


    # Сначала считаем прогресс
    for _, point in route_data.iterrows():

        point_id = get_point_id(
            point
        )

        if (
            point_id
            in st.session_state.completed_points
        ):

            completed_count += 1


    # =====================================================
    # ЗАГОЛОВОК МАРШРУТА
    # =====================================================

    st.divider()

    st.subheader(
        f"🚗 {route}"
    )


    # =====================================================
    # ПРОГРЕСС
    # =====================================================

    progress = 0

    if total_points > 0:

        progress = (
            completed_count
            / total_points
        )


    st.progress(progress)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Пройдено",
            completed_count
        )

    with col2:

        st.metric(
            "Осталось",
            total_points - completed_count
        )

    with col3:

        st.metric(
            "Всего ТТ",
            total_points
        )


    # =====================================================
    # ТОРГОВЫЕ ТОЧКИ
    # =====================================================

    for number, (
        index,
        point
    ) in enumerate(
        route_data.iterrows(),
        start=1
    ):

        point_id = get_point_id(
            point
        )


        # Проверяем статус
        is_completed = (
            point_id
            in st.session_state.completed_points
        )


        if is_completed:

            status = "🟢"

            status_text = "Пройдена"

        else:

            status = "🔴"

            status_text = "Не пройдена"


        # =================================================
        # БЛОК ТТ
        # =================================================

        with st.expander(

            f"{status} "
            f"{number}. "
            f"{point['Магазин']} — "
            f"{point['Адрес']} "
            f"({status_text})",

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


            # =============================================
            # ЕСЛИ ТТ ЕЩЁ НЕ ПРОЙДЕНА
            # =============================================

            if not is_completed:


                # -----------------------------------------
                # ФОТО
                # -----------------------------------------

                photos = st.file_uploader(

                    "📷 Добавить фотографии",

                    type=[
                        "jpg",
                        "jpeg",
                        "png"
                    ],

                    accept_multiple_files=True,

                    key=f"photos_{point_id}"
                )


                if photos:

                    st.info(
                        f"📷 Выбрано фотографий: "
                        f"{len(photos)}"
                    )


                    # Предварительный просмотр
                    preview_photos = photos[:4]

                    st.image(
                        preview_photos,
                        width=200
                    )


                # -----------------------------------------
                # КОММЕНТАРИЙ
                # -----------------------------------------

                comment = st.text_area(

                    "💬 Комментарий",

                    placeholder=(
                        "Например: товара нет, "
                        "малый остаток, "
                        "причина отсутствия..."
                    ),

                    key=f"comment_{point_id}"
                )


                # -----------------------------------------
                # КНОПКА ЗАВЕРШЕНИЯ
                # -----------------------------------------

                if st.button(

                    "✓ ЗАВЕРШИТЬ ТТ",

                    key=f"complete_{point_id}",

                    type="primary"

                ):


                    # Сохраняем статус
                    st.session_state.completed_points[
                        point_id
                    ] = True


                    # Сохраняем комментарий
                    st.session_state.point_comments[
                        point_id
                    ] = comment


                    # Сохраняем время
                    st.session_state.completion_times[
                        point_id
                    ] = datetime.now().strftime(
                        "%d.%m.%Y %H:%M"
                    )


                    # Пока фото сохраняются
                    # только в памяти приложения.
                    st.session_state.point_photos[
                        point_id
                    ] = photos


                    st.success(
                        "ТТ успешно завершена!"
                    )


                    st.rerun()


            # =============================================
            # ЕСЛИ ТТ УЖЕ ПРОЙДЕНА
            # =============================================

            else:

                st.success(
                    "🟢 ТТ пройдена"
                )


                # Время
                if (
                    point_id
                    in st.session_state.completion_times
                ):

                    st.write(
                        "🕒 **Время завершения:** "
                        + st.session_state.completion_times[
                            point_id
                        ]
                    )


                # Комментарий
                if (
                    point_id
                    in st.session_state.point_comments
                ):

                    saved_comment = (
                        st.session_state.point_comments[
                            point_id
                        ]
                    )


                    if saved_comment:

                        st.write(
                            "💬 **Комментарий:**"
                        )

                        st.write(
                            saved_comment
                        )


                # Фото
                if (
                    point_id
                    in st.session_state.point_photos
                ):

                    saved_photos = (
                        st.session_state.point_photos[
                            point_id
                        ]
                    )


                    if saved_photos:

                        st.write(
                            f"📷 **Фотографий:** "
                            f"{len(saved_photos)}"
                        )


                        st.image(
                            saved_photos,
                            width=200
                        )


# =========================================================
# ОБЩАЯ СТАТИСТИКА ЗА ВЫБРАННЫЙ ДЕНЬ
# =========================================================

st.divider()

st.subheader(
    "📊 Общий прогресс"
)


total_day_points = len(day_data)

completed_day_points = 0


for _, point in day_data.iterrows():

    point_id = get_point_id(
        point
    )

    if (
        point_id
        in st.session_state.completed_points
    ):

        completed_day_points += 1


if total_day_points > 0:

    total_progress = (
        completed_day_points
        / total_day_points
    )

    st.progress(
        total_progress
    )


col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Всего ТТ",
        total_day_points
    )

with col2:

    st.metric(
        "Пройдено",
        completed_day_points
    )

with col3:

    st.metric(
        "Осталось",
        total_day_points
        - completed_day_points
    )


# =========================================================
# ТЕСТОВАЯ ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ
# =========================================================

with st.expander(
    "🔧 Техническая информация"
):

    st.write(
        f"Дата отчёта: {date_key}"
    )

    st.write(
        f"Всего мерчендайзеров: "
        f"{len(workers)}"
    )

    st.write(
        "Эта версия пока работает "
        "в тестовом режиме."
    )

    st.write(
        "После перезапуска сервера "
        "статусы и фотографии могут исчезнуть."
    )
