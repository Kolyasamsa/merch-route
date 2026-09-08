import streamlit as st
import openpyxl
from datetime import datetime
import os


st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide"
)


# ==========================================
# ИМЯ EXCEL-ФАЙЛА
# ==========================================

EXCEL_FILE = "для проверки маршрут мерчей август (1).xlsx"


# ==========================================
# ДНИ И ИХ КОЛОНКИ В ТВОЁМ EXCEL
#
# Понедельник:
# A = сеть
# B = адрес
#
# Вторник:
# H = сеть
# I = адрес
#
# Среда:
# O = сеть
# P = адрес
#
# Четверг и пятница пока определим
# автоматически ниже.
# ==========================================

DAY_COLUMNS = {
    "Понедельник": (1, 2),
    "Вторник": (8, 9),
    "Среда": (15, 16),
}


@st.cache_data
def load_routes():

    routes = {}

    if not os.path.exists(EXCEL_FILE):
        return None

    workbook = openpyxl.load_workbook(
        EXCEL_FILE,
        data_only=False
    )

    for sheet_name in workbook.sheetnames:

        sheet = workbook[sheet_name]

        # Имя мерчендайзера находится в A1.
        worker_name = sheet["A1"].value

        if not worker_name:
            worker_name = sheet_name

        worker_name = str(worker_name).strip()

        routes[worker_name] = {
            "Понедельник": [],
            "Вторник": [],
            "Среда": [],
            "Четверг": [],
            "Пятница": []
        }

        # Читаем известные блоки маршрутов
        for day, columns in DAY_COLUMNS.items():

            shop_column = columns[0]
            address_column = columns[1]

            for row in range(3, sheet.max_row + 1):

                shop = sheet.cell(
                    row,
                    shop_column
                ).value

                address = sheet.cell(
                    row,
                    address_column
                ).value

                # Если есть и сеть, и адрес —
                # считаем это торговой точкой.
                if shop and address:

                    routes[worker_name][day].append({
                        "shop": str(shop).strip(),
                        "address": str(address).strip()
                    })

    return routes


# ==========================================
# ЗАГРУЖАЕМ МАРШРУТЫ
# ==========================================

routes = load_routes()


# ==========================================
# ЕСЛИ EXCEL НЕ НАЙДЕН
# ==========================================

if routes is None:

    st.error(
        "Excel-файл не найден. "
        "Проверь, что он загружен в GitHub "
        "и его название совпадает с названием "
        "в переменной EXCEL_FILE."
    )

    st.stop()


# ==========================================
# ОПРЕДЕЛЯЕМ СЕГОДНЯШНИЙ ДЕНЬ
# ==========================================

days = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]

today_number = datetime.today().weekday()

if today_number < 5:
    today = days[today_number]
else:
    today = "Понедельник"


# ==========================================
# ИНТЕРФЕЙС
# ==========================================

st.title("📍 Маршруты мерчендайзеров")

st.caption(
    "Маршруты автоматически загружаются из Excel"
)


# ==========================================
# ВЫБОР МЕРЧЕНДАЙЗЕРА
# ==========================================

worker = st.selectbox(
    "👤 Мерчендайзер",
    list(routes.keys())
)


# ==========================================
# ВЫБОР ДНЯ
# ==========================================

day = st.selectbox(
    "📅 День маршрута",
    days,
    index=days.index(today)
)


st.divider()


# ==========================================
# ВЫВОД МАРШРУТА
# ==========================================

points = routes[worker][day]

st.subheader(
    f"{worker} — {day}"
)

st.write(
    f"Всего ТТ в маршруте: "
    f"**{len(points)}**"
)


# ==========================================
# ВЫВОД ТОРГОВЫХ ТОЧЕК
# ==========================================

if len(points) == 0:

    st.warning(
        "Для этого дня пока "
        "не удалось найти ТТ."
    )

else:

    for number, point in enumerate(
        points,
        start=1
    ):

        st.write(
            f"**{number}. {point['shop']}**"
        )

        st.caption(
            f"📍 {point['address']}"
        )

        st.divider()


# ==========================================
# ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ
# ==========================================

with st.expander(
    "🔧 Проверка импорта"
):

    for worker_name, worker_routes in routes.items():

        st.write(
            f"**{worker_name}**"
        )

        for day_name, day_points in worker_routes.items():

            st.write(
                f"{day_name}: "
                f"{len(day_points)} ТТ"
            )
