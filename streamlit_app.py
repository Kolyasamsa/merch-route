from datetime import date

import streamlit as st

from auth import login, logout

from config import DAYS

from routes import (
load_routes,
get_worker_data,
get_available_days,
get_routes_for_day,
)

from database import (
get_completed_visits,
get_visit_photos,
create_visit,
upload_visit_photos,
replace_visit_photos,
reset_visit,
update_visit_comment,
clear_database_cache,
)

from utils import (
MONTHS,
get_point_key,
get_dates_for_weekday,
get_default_date,
)

# =========================================================

# НАСТРОЙКИ

# =========================================================

st.set_page_config(
page_title="Маршруты мерчендайзеров",
page_icon="📍",
layout="wide",
)

# =========================================================

# АВТОРИЗАЦИЯ

# =========================================================

worker = login()

if not worker:
st.stop()

# =========================================================

# ЗАГРУЗКА ДАННЫХ

# =========================================================

try:

```
df = load_routes()
```

except Exception as error:

```
st.error(
    f"Ошибка загрузки маршрутов: {error}"
)

st.stop()
```

# =========================================================

# ПРОВЕРКА МЕРЧЕНДАЙЗЕРА

# =========================================================

if worker not in df["Мерчендайзер"].unique():

```
st.error(
    f"Для мерчендайзера '{worker}' "
    "не найдены маршруты."
)

if st.button(
    "🚪 Выйти"
):

    logout()

st.stop()
```

# =========================================================

# ЗАГОЛОВОК

# =========================================================

col_title, col_logout = st.columns(
[4, 1]
)

with col_title:

```
st.title(
    "📍 Маршруты"
)

st.caption(
    f"👤 Мерчендайзер: {worker}"
)
```

with col_logout:

```
st.write("")

if st.button(

    "🚪 Выйти",

    use_container_width=True,
):

    logout()
```

# =========================================================

# ДАННЫЕ МЕРЧЕНДАЙЗЕРА

# =========================================================

worker_data = get_worker_data(
df,
worker,
)

available_days = get_available_days(
worker_data,
)

# =========================================================

# ВЫБОР ДНЯ

# =========================================================

today = date.today()

today_day_index = (
today.weekday()
)

default_day = (

```
DAYS[today_day_index]

if today_day_index < len(DAYS)

else available_days[0]
```

)

day_index = (

```
available_days.index(
    default_day
)

if default_day in available_days

else 0
```

)

day = st.selectbox(

```
"📅 День маршрута",

available_days,

index=day_index,
```

)

# =========================================================

# ВЫБОР ГОДА И МЕСЯЦА

# =========================================================

year_options = [

```
today.year - 1,

today.year,

today.year + 1,
```

]

year = st.selectbox(

```
"📅 Год",

year_options,

index=1,
```

)

month_name = st.selectbox(

```
"📅 Месяц",

MONTHS,

index=today.month - 1,
```

)

month = (

```
MONTHS.index(
    month_name
)

\+ 1
```

)

# =========================================================

# ДОСТУПНЫЕ ДАТЫ

# =========================================================

available_dates = (

```
get_dates_for_weekday(

    year,

    month,

    day,
)
```

)

default_date = (

```
get_default_date(
    available_dates
)
```

)

selected_date = st.selectbox(

```
"📆 Дата маршрута",

available_dates,

index=available_dates.index(
    default_date
),

format_func=lambda value:

    value.strftime(
        "%d.%m.%Y"
    ),
```

)

selected_date_string = (

```
selected_date.strftime(
    "%Y-%m-%d"
)
```

)

# =========================================================

# МАРШРУТЫ НА ДЕНЬ

# =========================================================

day_data, routes = (

```
get_routes_for_day(

    worker_data,

    day,
)
```

)

# =========================================================

# ЗАГРУЖАЕМ ПРОЙДЕННЫЕ ТТ

# =========================================================

try:

```
visits = (

    get_completed_visits(

        selected_date_string,

        worker,
    )
)
```

except Exception as error:

```
st.error(
    f"Ошибка загрузки прохождений: {error}"
)

visits = []
```

# =========================================================

# СЛОВАРЬ ПРОЙДЕННЫХ ТТ

# =========================================================

completed_visits = {

```
get_point_key(

    visit["worker"],

    visit["weekday"],

    visit["route"],

    visit["shop"],

    visit["address"],
): visit

for visit in visits
```

}

# =========================================================

# ОБЩАЯ ИНФОРМАЦИЯ

# =========================================================

st.divider()

st.subheader(
f"👤 {worker}"
)

st.write(

```
f"📅 **{day}, "
f"{selected_date.strftime('%d.%m.%Y')}**"
```

)

st.write(
f"Маршрутов: **{len(routes)}**"
)

st.write(
f"Всего ТТ: **{len(day_data)}**"
)

# =========================================================

# ВЫВОД МАРШРУТОВ

# =========================================================

for route in routes:

```
route_data = day_data[

    day_data["Маршрут"] == route
]


total_points = len(
    route_data
)


# -----------------------------------------------------
# ПОДСЧЁТ ПРОЙДЕННЫХ ТТ
# -----------------------------------------------------

completed_count = sum(

    get_point_key(

        worker,

        day,

        route,

        point["Магазин"],

        point["Адрес"],
    )

    in completed_visits

    for _, point

    in route_data.iterrows()
)


# -----------------------------------------------------
# ЗАГОЛОВОК МАРШРУТА
# -----------------------------------------------------

st.divider()


st.subheader(
    f"🚗 {route}"
)


st.progress(

    completed_count / total_points

    if total_points

    else 0
)


col1, col2, col3 = st.columns(3)


col1.metric(

    "Пройдено",

    completed_count,
)


col2.metric(

    "Осталось",

    total_points - completed_count,
)


col3.metric(

    "Всего",

    total_points,
)


# =====================================================
# ТОРГОВЫЕ ТОЧКИ
# =====================================================

for number, (

    _,

    point,

) in enumerate(

    route_data.iterrows(),

    start=1,
):


    shop = point[
        "Магазин"
    ]


    address = point[
        "Адрес"
    ]


    point_key = get_point_key(

        worker,

        day,

        route,

        shop,

        address,
    )


    visit = (

        completed_visits.get(
            point_key
        )
    )


    is_completed = (

        visit is not None
    )


    status = (

        "🟢"

        if is_completed

        else "🔴"
    )


    status_text = (

        "Пройдена"

        if is_completed

        else "Не пройдена"
    )


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
                    "png",
                ],

                accept_multiple_files=True,

                key=(
                    f"photos_{point_key}"
                ),
            )


            comment = st.text_area(

                "💬 Комментарий",

                placeholder=(

                    "Например: товара нет, "
                    "малый остаток, "
                    "причина отсутствия..."
                ),

                key=(
                    f"comment_{point_key}"
                ),
            )


            if st.button(

                "✓ ЗАВЕРШИТЬ ТТ",

                key=(
                    f"complete_{point_key}"
                ),

                type="primary",

                use_container_width=True,
            ):


                try:


                    new_visit = (

                        create_visit(

                            selected_date_string,

                            worker,

                            day,

                            route,

                            shop,

                            address,

                            comment,
                        )
                    )


                    visit_id = (
                        new_visit["id"]
                    )


                    upload_visit_photos(

                        photos,

                        visit_id,
                    )


                    clear_database_cache()


                    st.rerun()


                except Exception as error:


                    st.error(
                        f"Ошибка сохранения: {error}"
                    )


        # =============================================
        # ПРОЙДЕНА
        # =============================================

        else:


            st.success(
                "🟢 ТТ пройдена"
            )


            # =============================================
            # КОММЕНТАРИЙ
            # =============================================

            st.divider()


            st.write(
                "💬 **Комментарий:**"
            )


            edit_mode_key = (
                f"edit_mode_{visit['id']}"
            )


            if edit_mode_key not in st.session_state:

                st.session_state[
                    edit_mode_key
                ] = False


            # =============================================
            # ОБЫЧНЫЙ РЕЖИМ
            # =============================================

            if not st.session_state[
                edit_mode_key
            ]:


                saved_comment = visit.get(

                    "comment",

                    "",
                )


                if saved_comment:

                    st.write(
                        saved_comment
                    )


                else:

                    st.caption(
                        "Комментарий отсутствует"
                    )


                if st.button(

                    "✏️ Редактировать комментарий",

                    key=(
                        f"edit_button_"
                        f"{visit['id']}"
                    ),

                    use_container_width=True,
                ):


                    st.session_state[
                        edit_mode_key
                    ] = True


                    st.rerun()


            # =============================================
            # РЕЖИМ РЕДАКТИРОВАНИЯ
            # =============================================

            else:


                edited_comment = st.text_area(

                    "Комментарий к ТТ",

                    value=visit.get(

                        "comment",

                        "",
                    ),

                    key=(
                        f"edit_comment_"
                        f"{visit['id']}"
                    ),
                )


                col_save, col_cancel = (
                    st.columns(2)
                )


                with col_save:


                    if st.button(

                        "💾 Сохранить",

                        key=(
                            f"save_comment_"
                            f"{visit['id']}"
                        ),

                        use_container_width=True,
                    ):


                        try:


                            update_visit_comment(

                                visit["id"],

                                edited_comment,
                            )


                            st.session_state[
                                edit_mode_key
                            ] = False


                            st.rerun()


                        except Exception as error:


                            st.error(

                                f"Ошибка сохранения "
                                f"комментария: {error}"
                            )


                with col_cancel:


                    if st.button(

                        "✖ Отмена",

                        key=(
                            f"cancel_edit_"
                            f"{visit['id']}"
                        ),

                        use_container_width=True,
                    ):


                        st.session_state[
                            edit_mode_key
                        ] = False


                        st.rerun()


            # =============================================
            # ВРЕМЯ ПРОХОЖДЕНИЯ
            # =============================================

            if visit.get(
                "completed_at"
            ):


                st.write(

                    f"🕒 **Время:** "
                    f"{visit['completed_at']}"
                )


            # =============================================
            # ФОТОГРАФИИ
            # =============================================

            st.divider()


            photo_edit_mode_key = (

                f"photo_edit_mode_"
                f"{visit['id']}"
            )


            if photo_edit_mode_key not in st.session_state:

                st.session_state[
                    photo_edit_mode_key
                ] = False


            try:


                saved_photos = (

                    get_visit_photos(
                        visit["id"]
                    )
                )


                # =========================================
                # ОБЫЧНЫЙ РЕЖИМ
                # =========================================

                if not st.session_state[
                    photo_edit_mode_key
                ]:


                    if saved_photos:


                        st.write(
                            "📷 **Фотографии:**"
                        )


                        columns = (
                            st.columns(3)
                        )


                        for index, photo in enumerate(

                            saved_photos

                        ):


                            with columns[
                                index % 3
                            ]:


                                st.image(

                                    photo[
                                        "public_url"
                                    ],

                                    use_container_width=True,
                                )


                    else:


                        st.info(
                            "К этой ТТ нет фотографий."
                        )


                    if st.button(

                        "✏️ Заменить фотографии",

                        key=(
                            f"edit_photos_"
                            f"{visit['id']}"
                        ),

                        use_container_width=True,
                    ):


                        st.session_state[
                            photo_edit_mode_key
                        ] = True


                        st.rerun()


                # =========================================
                # РЕЖИМ ЗАМЕНЫ
                # =========================================

                else:


                    st.write(
                        "✏️ **Замена фотографий**"
                    )


                    if saved_photos:


                        st.caption(
                            "Текущие фотографии:"
                        )


                        columns = (
                            st.columns(3)
                        )


                        for index, photo in enumerate(

                            saved_photos

                        ):


                            with columns[
                                index % 3
                            ]:


                                st.image(

                                    photo[
                                        "public_url"
                                    ],

                                    use_container_width=True,
                                )


                    new_photos = (

                        st.file_uploader(

                            "📷 Выберите новые фотографии",

                            type=[
                                "jpg",
                                "jpeg",
                                "png",
                            ],

                            accept_multiple_files=True,

                            key=(
                                f"replace_photos_"
                                f"{visit['id']}"
                            ),
                        )
                    )


                    col_replace, col_cancel = (

                        st.columns(2)
                    )


                    # =====================================
                    # ЗАМЕНИТЬ
                    # =====================================

                    with col_replace:


                        if st.button(

                            "💾 Заменить",

                            key=(
                                f"save_photos_"
                                f"{visit['id']}"
                            ),

                            use_container_width=True,
                        ):


                            if not new_photos:


                                st.warning(

                                    "Выберите хотя бы "
                                    "одну фотографию."
                                )


                            else:


                                try:


                                    replace_visit_photos(

                                        new_photos,

                                        visit["id"],
                                    )


                                    st.session_state[
                                        photo_edit_mode_key
                                    ] = False


                                    st.rerun()


                                except Exception as error:


                                    st.error(

                                        f"Ошибка замены "
                                        f"фотографий: "
                                        f"{error}"
                                    )


                    # =====================================
                    # ОТМЕНА
                    # =====================================

                    with col_cancel:


                        if st.button(

                            "✖ Отмена",

                            key=(
                                f"cancel_photos_"
                                f"{visit['id']}"
                            ),

                            use_container_width=True,
                        ):


                            st.session_state[
                                photo_edit_mode_key
                            ] = False


                            st.rerun()


            except Exception as error:


                st.warning(

                    f"Не удалось загрузить фотографии: "
                    f"{error}"
                )


            # =============================================
            # СБРОС ПРОХОЖДЕНИЯ
            # =============================================

            st.divider()


            if st.button(

                "↩️ СБРОСИТЬ ПРОХОЖДЕНИЕ ТТ",

                key=(
                    f"reset_{point_key}"
                ),

                use_container_width=True,
            ):


                try:


                    reset_visit(
                        visit["id"]
                    )


                    clear_database_cache()


                    st.rerun()


                except Exception as error:


                    st.error(
                        f"Ошибка сброса ТТ: {error}"
                    )
```

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

completed_points = sum(

```
get_point_key(

    worker,

    day,

    point["Маршрут"],

    point["Магазин"],

    point["Адрес"],
)

in completed_visits

for _, point

in day_data.iterrows()
```

)

progress = (

```
completed_points / total_points

if total_points

else 0
```

)

st.progress(
progress
)

col1, col2, col3 = st.columns(3)

col1.metric(

```
"Всего ТТ",

total_points,
```

)

col2.metric(

```
"Пройдено",

completed_points,
```

)

col3.metric(

```
"Осталось",

total_points - completed_points,
```

)
