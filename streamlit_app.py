import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import uuid

from supabase import create_client


# =========================================================
# НАСТРОЙКИ
# =========================================================

st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide"
)

EXCEL_FILE = "routes.xlsx"

DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# ЗАГРУЗКА EXCEL
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
                f"В Excel отсутствует столбец: {column}"
            )

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# ЗАГРУЖАЕМ EXCEL
# =========================================================

try:
    df = load_routes()

except Exception as e:
    st.error(f"Ошибка чтения Excel: {e}")
    st.stop()


if df is None:
    st.error(f"Файл {EXCEL_FILE} не найден.")
    st.stop()


# =========================================================
# УНИКАЛЬНЫЙ КЛЮЧ ТТ
# =========================================================

def get_point_key(
    worker,
    day,
    route,
    shop,
    address
):

    return (
        f"{worker}|"
        f"{day}|"
        f"{route}|"
        f"{shop}|"
        f"{address}"
    )


# =========================================================
# ПОЛУЧЕНИЕ ПРОЙДЕННЫХ ТТ
# =========================================================

@st.cache_data(ttl=10)
def get_completed_visits(
    selected_date_string,
    worker
):

    response = (
        supabase
        .table("point_visits")
        .select("*")
        .eq(
            "visit_date",
            selected_date_string
        )
        .eq(
            "worker",
            worker
        )
        .execute()
    )

    return response.data


# =========================================================
# ПОЛУЧЕНИЕ ФОТО КОНКРЕТНОЙ ТТ
# =========================================================

@st.cache_data(ttl=10)
def get_visit_photos(
    visit_id
):

    response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq(
            "visit_id",
            str(visit_id)
        )
        .order(
            "created_at"
        )
        .execute()
    )

    return response.data


# =========================================================
# СОЗДАНИЕ ТТ В БАЗЕ
# =========================================================

def save_visit(
    selected_date_string,
    worker,
    day,
    route,
    shop,
    address,
    comment
):

    data = {
        "visit_date": selected_date_string,
        "worker": worker,
        "weekday": day,
        "route": route,
        "shop": shop,
        "address": address,
        "completed": True,
        "comment": comment,
        "completed_at": datetime.now().isoformat()
    }

    response = (
        supabase
        .table("point_visits")
        .insert(data)
        .execute()
    )

    if not response.data:
        raise Exception(
            "Supabase не вернул данные созданной ТТ"
        )

    return response.data[0]


# =========================================================
# ЗАГРУЗКА ФОТО И СОХРАНЕНИЕ В БАЗЕ
# =========================================================

def upload_photos(
    files,
    visit_id
):

    uploaded_files = []

    if not files:
        return uploaded_files


    for file in files:


        # =============================================
        # РАСШИРЕНИЕ ФАЙЛА
        # =============================================

        if "." in file.name:

            file_extension = (
                file.name
                .rsplit(".", 1)[-1]
                .lower()
            )

        else:

            file_extension = "jpg"


        # =============================================
        # УНИКАЛЬНОЕ ИМЯ
        # =============================================

        file_name = (
            f"{uuid.uuid4()}.{file_extension}"
        )


        # =============================================
        # ПАПКА КОНКРЕТНОЙ ТТ
        #
        # Используем UUID ТТ,
        # поэтому никаких проблем с кириллицей.
        # =============================================

        file_path = (
            f"visits/"
            f"{visit_id}/"
            f"{file_name}"
        )


        # =============================================
        # ЗАГРУЗКА В STORAGE
        # =============================================

        supabase.storage.from_(
            "point-photos"
        ).upload(
            path=file_path,
            file=file.getvalue(),
            file_options={
                "content-type": file.type
            }
        )


        # =============================================
        # ПУБЛИЧНАЯ ССЫЛКА
        # =============================================

        public_url = (
            supabase
            .storage
            .from_(
                "point-photos"
            )
            .get_public_url(
                file_path
            )
        )


        # =============================================
        # СОХРАНЯЕМ ФОТО В БАЗУ
        # =============================================

        photo_data = {
            "visit_id": str(visit_id),
            "file_path": file_path,
            "public_url": public_url
        }


        (
            supabase
            .table("point_photos")
            .insert(photo_data)
            .execute()
        )


        uploaded_files.append(
            public_url
        )


    return uploaded_files


# =========================================================
# СБРОС ТТ И УДАЛЕНИЕ ФОТО
# =========================================================

def reset_visit(
    visit_id
):


    # =====================================================
    # ПОЛУЧАЕМ ФОТО
    # =====================================================

    response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq(
            "visit_id",
            str(visit_id)
        )
        .execute()
    )


    photos = response.data


    # =====================================================
    # УДАЛЯЕМ ФАЙЛЫ ИЗ STORAGE
    # =====================================================

    if photos:

        file_paths = [
            photo["file_path"]
            for photo in photos
        ]


        supabase.storage.from_(
            "point-photos"
        ).remove(
            file_paths
        )


    # =====================================================
    # УДАЛЯЕМ ЗАПИСИ О ФОТО
    # =====================================================

    (
        supabase
        .table("point_photos")
        .delete()
        .eq(
            "visit_id",
            str(visit_id)
        )
        .execute()
    )


    # =====================================================
    # УДАЛЯЕМ ТТ
    # =====================================================

    (
        supabase
        .table("point_visits")
        .delete()
        .eq(
            "id",
            str(visit_id)
        )
        .execute()
    )


# =========================================================
# ОПРЕДЕЛЯЕМ ДЕНЬ НЕДЕЛИ
# =========================================================

weekday_number = datetime.today().weekday()

if weekday_number < 5:
    today_day = DAYS[weekday_number]
else:
    today_day = "Понедельник"


# =========================================================
# ЗАГОЛОВОК
# =========================================================

st.title(
    "📍 Маршруты мерчендайзеров"
)

st.caption(
    "Контроль прохождения торговых точек"
)


# =========================================================
# ВЫБОР МЕРЧЕНДАЙЗЕРА
# =========================================================

workers = sorted(
    df["Мерчендайзер"]
    .unique()
    .tolist()
)


worker = st.selectbox(
    "👤 Мерчендайзер",
    workers
)


# =========================================================
# ДОСТУПНЫЕ ДНИ
# =========================================================

worker_data = df[
    df["Мерчендайзер"] == worker
]


available_days = [

    day

    for day in DAYS

    if day in worker_data[
        "День"
    ].unique()

]


if today_day in available_days:

    default_day_index = (
        available_days.index(
            today_day
        )
    )

else:

    default_day_index = 0


day = st.selectbox(
    "📅 День маршрута",
    available_days,
    index=default_day_index
)


# =========================================================
# ДАТА
# =========================================================

selected_date = st.date_input(
    "📅 Дата прохождения",
    value=date.today(),
    format="DD.MM.YYYY"
)


selected_date_string = (
    selected_date.strftime(
        "%Y-%m-%d"
    )
)


# =========================================================
# ФИЛЬТРУЕМ ТТ
# =========================================================

day_data = worker_data[
    worker_data["День"] == day
].copy()


routes = (
    day_data[
        "Маршрут"
    ]
    .dropna()
    .unique()
    .tolist()
)


# =========================================================
# ЗАГРУЖАЕМ ПРОЙДЕННЫЕ ТТ
# =========================================================

try:

    visits = get_completed_visits(
        selected_date_string,
        worker
    )

except Exception as e:

    st.error(
        f"Ошибка загрузки ТТ: {e}"
    )

    visits = []


# =========================================================
# СЛОВАРЬ ПРОЙДЕННЫХ ТТ
# =========================================================

completed_visits = {}


for visit in visits:

    key = get_point_key(

        visit["worker"],

        visit["weekday"],

        visit["route"],

        visit["shop"],

        visit["address"]

    )

    completed_visits[key] = visit


# =========================================================
# ИНФОРМАЦИЯ
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
# МАРШРУТЫ
# =========================================================

for route in routes:


    route_data = day_data[
        day_data["Маршрут"] == route
    ]


    total_points = len(
        route_data
    )


    completed_count = 0


    for _, point in route_data.iterrows():

        point_key = get_point_key(

            worker,
            day,
            route,
            point["Магазин"],
            point["Адрес"]

        )


        if point_key in completed_visits:

            completed_count += 1


    progress = 0


    if total_points > 0:

        progress = (
            completed_count
            / total_points
        )


    # =====================================================
    # ЗАГОЛОВОК МАРШРУТА
    # =====================================================

    st.divider()

    st.subheader(
        f"🚗 {route}"
    )

    st.progress(
        progress
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Пройдено",
        completed_count
    )

    col2.metric(
        "Осталось",
        total_points - completed_count
    )

    col3.metric(
        "Всего",
        total_points
    )


    # =====================================================
    # ТОРГОВЫЕ ТОЧКИ
    # =====================================================

    for number, (
        _,
        point
    ) in enumerate(
        route_data.iterrows(),
        start=1
    ):


        shop = point["Магазин"]
        address = point["Адрес"]


        point_key = get_point_key(

            worker,
            day,
            route,
            shop,
            address

        )


        is_completed = (
            point_key
            in completed_visits
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
            f"{shop} — "
            f"{address} "
            f"({status_text})"

        ):


            st.write(
                f"🏪 **Магазин:** {shop}"
            )

            st.write(
                f"📍 **Адрес:** {address}"
            )


            # =============================================
            # НЕ ПРОЙДЕНА
            # =============================================

            if not is_completed:


                photos = st.file_uploader(

                    "📷 Добавить фотографии",

                    type=[
                        "jpg",
                        "jpeg",
                        "png"
                    ],

                    accept_multiple_files=True,

                    key=(
                        f"photos_"
                        f"{point_key}"
                    )

                )


                comment = st.text_area(

                    "💬 Комментарий",

                    placeholder=(
                        "Например: товара нет, "
                        "малый остаток, "
                        "причина отсутствия..."
                    ),

                    key=(
                        f"comment_"
                        f"{point_key}"
                    )

                )


                if st.button(

                    "✓ ЗАВЕРШИТЬ ТТ",

                    key=(
                        f"complete_"
                        f"{point_key}"
                    ),

                    type="primary"

                ):


                    try:


                        # =================================
                        # СОЗДАЁМ ТТ
                        # =================================

                        new_visit = save_visit(

                            selected_date_string,
                            worker,
                            day,
                            route,
                            shop,
                            address,
                            comment

                        )


                        # Получаем UUID созданной ТТ

                        visit_id = (
                            new_visit["id"]
                        )


                        # =================================
                        # ЗАГРУЖАЕМ ФОТО
                        # =================================

                        if photos:

                            upload_photos(

                                photos,
                                visit_id

                            )


                        # =================================
                        # ОБНОВЛЯЕМ ДАННЫЕ
                        # =================================

                        get_completed_visits.clear()
                        get_visit_photos.clear()


                        st.success(
                            "ТТ сохранена!"
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Ошибка сохранения: {e}"
                        )


            # =============================================
            # ПРОЙДЕНА
            # =============================================

            else:


                visit = (
                    completed_visits[
                        point_key
                    ]
                )


                visit_id = (
                    visit["id"]
                )


                st.success(
                    "🟢 ТТ пройдена"
                )


                # =========================================
                # ВРЕМЯ
                # =========================================

                if visit.get(
                    "completed_at"
                ):

                    st.write(
                        f"🕒 **Время:** "
                        f"{visit['completed_at']}"
                    )


                # =========================================
                # КОММЕНТАРИЙ
                # =========================================

                if visit.get(
                    "comment"
                ):

                    st.write(
                        "💬 **Комментарий:**"
                    )

                    st.write(
                        visit["comment"]
                    )


                # =========================================
                # ФОТО
                # =========================================

                try:

                    saved_photos = (
                        get_visit_photos(
                            visit_id
                        )
                    )


                    if saved_photos:

                        st.divider()

                        st.write(
                            "📷 **Фотографии:**"
                        )


                        photo_columns = (
                            st.columns(3)
                        )


                        for index, photo in enumerate(
                            saved_photos
                        ):

                            with photo_columns[
                                index % 3
                            ]:

                                st.image(
                                    photo[
                                        "public_url"
                                    ],
                                    use_container_width=True
                                )


                    else:

                        st.info(
                            "К этой ТТ пока нет фотографий."
                        )


                except Exception as e:

                    st.warning(
                        f"Не удалось загрузить фотографии: {e}"
                    )


                # =========================================
                # СБРОС ТТ
                # =========================================

                st.divider()


                if st.button(

                    "↩️ СБРОСИТЬ ПРОХОЖДЕНИЕ ТТ",

                    key=(
                        f"reset_"
                        f"{point_key}"
                    ),

                    use_container_width=True

                ):


                    try:


                        reset_visit(
                            visit_id
                        )


                        # Очищаем кэш

                        get_completed_visits.clear()
                        get_visit_photos.clear()


                        st.success(
                            "ТТ и связанные фотографии удалены."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Ошибка сброса ТТ: {e}"
                        )


# =========================================================
# ОБЩИЙ ПРОГРЕСС
# =========================================================

st.divider()

st.subheader(
    "📊 Общий прогресс"
)


total_points = len(
    day_data
)


completed_points = 0


for _, point in day_data.iterrows():

    point_key = get_point_key(

        worker,
        day,
        point["Маршрут"],
        point["Магазин"],
        point["Адрес"]

    )


    if point_key in completed_visits:

        completed_points += 1


if total_points > 0:

    st.progress(
        completed_points
        / total_points
    )


col1, col2, col3 = st.columns(3)


col1.metric(
    "Всего ТТ",
    total_points
)

col2.metric(
    "Пройдено",
    completed_points
)

col3.metric(
    "Осталось",
    total_points
    - completed_points
)
