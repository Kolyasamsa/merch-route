import streamlit as st
from datetime import datetime

# ==========================================
# НАСТРОЙКИ СТРАНИЦЫ
# ==========================================

st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide"
)


# ==========================================
# МАРШРУТЫ
#
# Здесь позже будут реальные маршруты.
# Каждый мерчендайзер имеет 5 маршрутов:
# Понедельник - Пятница
# ==========================================

routes = {

    "Олеся": {

        "Понедельник": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 1"
            },
            {
                "shop": "Пятерочка",
                "address": "Адрес 2"
            },
            {
                "shop": "Монетка",
                "address": "Адрес 3"
            }
        ],

        "Вторник": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 4"
            },
            {
                "shop": "Монетка",
                "address": "Адрес 5"
            }
        ],

        "Среда": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 6"
            }
        ],

        "Четверг": [
            {
                "shop": "Монетка",
                "address": "Адрес 7"
            }
        ],

        "Пятница": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 8"
            }
        ]
    },


    "Владимир": {

        "Понедельник": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 1"
            }
        ],

        "Вторник": [
            {
                "shop": "Монетка",
                "address": "Адрес 2"
            }
        ],

        "Среда": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 3"
            }
        ],

        "Четверг": [
            {
                "shop": "Пятерочка",
                "address": "Адрес 4"
            }
        ],

        "Пятница": [
            {
                "shop": "Монетка",
                "address": "Адрес 5"
            }
        ]
    }
}


# ==========================================
# ДНИ НЕДЕЛИ
# Python считает:
# Понедельник = 0
# Вторник = 1
# ...
# Пятница = 4
# ==========================================

days = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]


# Определяем сегодняшний день
today_number = datetime.today().weekday()

if today_number < 5:
    today = days[today_number]
else:
    today = None


# ==========================================
# СОСТОЯНИЕ ПРИЛОЖЕНИЯ
# ==========================================

if "completed" not in st.session_state:
    st.session_state.completed = {}

if "photos" not in st.session_state:
    st.session_state.photos = {}

if "comments" not in st.session_state:
    st.session_state.comments = {}


# ==========================================
# ЗАГОЛОВОК
# ==========================================

st.title("📍 Маршруты мерчендайзеров")

st.caption(
    "Загрузка фотографий и контроль прохождения торговых точек"
)


# ==========================================
# ВЫБОР МЕРЧЕНДАЙЗЕРА
# ==========================================

worker = st.selectbox(
    "👤 Выберите мерчендайзера",
    list(routes.keys())
)


# ==========================================
# ВЫБОР ДНЯ
# ==========================================

# Если сегодня рабочий день — автоматически
# выбираем сегодняшний день.
# Но пока можно переключать день вручную.

if today in days:
    default_day_index = days.index(today)
else:
    default_day_index = 0


day = st.selectbox(
    "📅 День маршрута",
    days,
    index=default_day_index
)


st.divider()


# ==========================================
# ИНФОРМАЦИЯ О МАРШРУТЕ
# ==========================================

st.subheader(f"👤 {worker}")

st.write(f"📅 **Маршрут: {day}**")

points = routes[worker][day]

total_points = len(points)

completed_count = 0


# ==========================================
# ТОРГОВЫЕ ТОЧКИ
# ==========================================

for i, point in enumerate(points):

    # Уникальный ID ТТ.
    # Добавляем мерчендайзера и день,
    # чтобы одна и та же ТТ в разных
    # маршрутах не путалась.

    point_id = f"{worker}_{day}_{i}"

    # Проверяем статус

    if point_id in st.session_state.completed:

        status = "🟢 Пройдена"
        completed_count += 1

    else:

        status = "🔴 Не пройдена"


    # ======================================
    # ОТКРЫВАЮЩИЙСЯ БЛОК ТТ
    # ======================================

    with st.expander(
        f"{status} — {point['shop']} — {point['address']}",
        expanded=False
    ):

        st.write(f"🏪 **Магазин:** {point['shop']}")

        st.write(f"📍 **Адрес:** {point['address']}")


        # ==================================
        # ЗАГРУЗКА ФОТО
        # ==================================

        uploaded_photos = st.file_uploader(

            "📷 Загрузить фотографии",

            type=[
                "jpg",
                "jpeg",
                "png"
            ],

            accept_multiple_files=True,

            key=f"upload_{point_id}"
        )


        # ==================================
        # КОММЕНТАРИЙ
        # ==================================

        comment = st.text_area(

            "💬 Комментарий",

            placeholder=
            "Например: товара нет, "
            "малый остаток, причина отсутствия товара...",

            key=f"comment_{point_id}"
        )


        # ==================================
        # ИНФОРМАЦИЯ О ФОТО
        # ==================================

        if uploaded_photos:

            st.info(
                f"📷 Загружено фотографий: "
                f"{len(uploaded_photos)}"
            )


        # ==================================
        # ЗАВЕРШЕНИЕ ТТ
        # ==================================

        if st.button(

            "✓ Завершить ТТ",

            key=f"complete_{point_id}"

        ):

            # Пока сохраняем только
            # в памяти приложения.
            # В следующей версии
            # подключим базу данных.

            st.session_state.completed[point_id] = {

                "worker": worker,

                "day": day,

                "shop": point["shop"],

                "address": point["address"],

                "completed_time":
                datetime.now().strftime(
                    "%d.%m.%Y %H:%M"
                )

            }


            st.session_state.photos[
                point_id
            ] = uploaded_photos


            st.session_state.comments[
                point_id
            ] = comment


            st.success(
                "Торговая точка отмечена "
                "как пройденная"
            )


            st.rerun()


        # ==================================
        # ЕСЛИ ТТ УЖЕ ПРОЙДЕНА
        # ==================================

        if point_id in st.session_state.completed:

            completed_data = (
                st.session_state.completed[
                    point_id
                ]
            )


            st.success(
                "🟢 ТТ пройдена"
            )


            st.write(
                "🕒 Время завершения: "
                + completed_data[
                    "completed_time"
                ]
            )


# ==========================================
# ПРОГРЕСС МАРШРУТА
# ==========================================

st.divider()

st.subheader("📊 Прогресс маршрута")


if total_points > 0:

    progress = (
        completed_count /
        total_points
    )

    st.progress(progress)

    st.write(
        f"**Пройдено: "
        f"{completed_count} "
        f"из {total_points} ТТ**"
    )


else:

    st.warning(
        "Для этого маршрута пока "
        "не добавлены торговые точки."
    )
