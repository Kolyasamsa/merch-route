from datetime import date

import streamlit as st

from auth import login, logout

from supervisor import (
    show_supervisor_dashboard,
)

from config import DAYS

from routes import (
    load_routes,
    get_workers,
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
    get_visit_comments,
    create_visit_comment,
)

from utils import (
    MONTHS,
    get_point_key,
    get_dates_for_weekday,
    get_default_date,
)


st.set_page_config(
    page_title="Маршруты мерчендайзеров",
    page_icon="📍",
    layout="wide",
)


user_name, user_role = login()

if not user_name:
    st.stop()


try:

    df = load_routes()

except Exception as error:

    st.error(
        f"Ошибка загрузки маршрутов: {error}"
    )

    st.stop()


if user_role == "supervisor":

    show_supervisor_dashboard(
        df,
        user_name,
        logout,
    )

    st.stop()


worker = user_name


if worker not in df["Мерчендайзер"].unique():

    st.error(
        f"Для мерчендайзера '{worker}' "
        "не найдены маршруты."
    )

    if st.button(
        "🚪 Выйти"
    ):
        logout()

    st.stop()


col_title, col_logout = st.columns(
    [4, 1]
)


with col_title:

    st.title(
        "📍 Маршруты"
    )

    st.caption(
        f"👤 Мерчендайзер: {worker}"
    )


with col_logout:

    st.write("")

    if st.button(
        "🚪 Выйти",
        use_container_width=True,
    ):

        logout()


worker_data = get_worker_data(
    df,
    worker,
)


available_days = get_available_days(
    worker_data,
)


today = date.today()

today_day_index = today.weekday()


default_day = (

    DAYS[today_day_index]

    if today_day_index < len(DAYS)

    else available_days[0]
)


day_index = (

    available_days.index(
        default_day
    )

    if default_day in available_days

    else 0
)


day = st.selectbox(
    "📅 День маршрута",
    available_days,
    index=day_index,
)


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


month_name = st.selectbox(
    "📅 Месяц",
    MONTHS,
    index=today.month - 1,
)


month = (
    MONTHS.index(
        month_name
    )
    + 1
)


available_dates = (
    get_dates_for_weekday(
        year,
        month,
        day,
    )
)


default_date = (
    get_default_date(
        available_dates
    )
)


selected_date = st.selectbox(
    "📆 Дата маршрута",
    available_dates,
    index=available_dates.index(
        default_date
    ),
    format_func=lambda value: (
        value.strftime(
            "%d.%m.%Y"
        )
    ),
)


selected_date_string = (
    selected_date.strftime(
        "%Y-%m-%d"
    )
)


day_data, routes = (
    get_routes_for_day(
        worker_data,
        day,
    )
)


try:

    visits = (
        get_completed_visits(
            selected_date_string,
            worker,
        )
    )

except Exception as error:

    st.error(
        f"Ошибка загрузки прохождений: {error}"
    )

    visits = []


completed_visits = {

    get_point_key(
        visit["worker"],
        visit["weekday"],
        visit["route"],
        visit["shop"],
        visit["address"],
    ): visit

    for visit in visits
}


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


for route in routes:

    route_data = day_data[
        day_data["Маршрут"] == route
    ]


    total_points = len(
        route_data
    )


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


    for number, (_, point) in enumerate(
        route_data.iterrows(),
        start=1,
    ):

        shop = point["Магазин"]

        address = point["Адрес"]


        point_key = get_point_key(
            worker,
            day,
            route,
            shop,
            address,
        )


        visit = (
            completed_visits
            .get(point_key)
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

                    if not photos:

                        st.warning(
                            "📷 Добавьте хотя бы одну "
                            "фотографию перед завершением ТТ."
                        )

                    else:

                        try:

                            new_visit = create_visit(
                                selected_date_string,
                                worker,
                                day,
                                route,
                                shop,
                                address,
                                comment,
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


            else:

                st.success(
                    "🟢 ТТ пройдена"
                )


                # =============================================
                # ФОТОГРАФИИ
                # =============================================

                st.divider()

                st.write(
                    "📷 **Фотографии**"
                )


                photo_edit_mode_key = (
                    f"photo_edit_mode_{visit['id']}"
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


                    if not st.session_state[
                        photo_edit_mode_key
                    ]:

                        if saved_photos:

                            columns = st.columns(3)


                            for index, photo in enumerate(
                                saved_photos
                            ):

                                with columns[
                                    index % 3
                                ]:

                                    st.image(
                                        photo["public_url"],
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


                    else:

                        st.write(
                            "✏️ **Замена фотографий**"
                        )


                        if saved_photos:

                            st.caption(
                                "Текущие фотографии:"
                            )


                            columns = st.columns(3)


                            for index, photo in enumerate(
                                saved_photos
                            ):

                                with columns[
                                    index % 3
                                ]:

                                    st.image(
                                        photo["public_url"],
                                        use_container_width=True,
                                    )


                        new_photos = st.file_uploader(
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


                        col_replace, col_cancel = (
                            st.columns(2)
                        )


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
                                            f"фотографий: {error}"
                                        )


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
                # КОММЕНТАРИЙ МЕРЧЕНДАЙЗЕРА
                # =============================================

                st.divider()


                st.write(
                    "📝 **Комментарий мерчендайзера**"
                )


                edit_mode_key = (
                    f"edit_mode_{visit['id']}"
                )


                if edit_mode_key not in st.session_state:

                    st.session_state[
                        edit_mode_key
                    ] = False


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
                # ОБСУЖДЕНИЕ С СУПЕРВАЙЗЕРОМ
                # =============================================

                st.divider()


                st.write(
                    "💬 **Обсуждение с супервайзером**"
                )


                try:

                    visit_comments = (
                        get_visit_comments(
                            visit["id"]
                        )
                    )


                    if visit_comments:

                        for visit_comment in visit_comments:

                            author = (
                                visit_comment.get(
                                    "author",
                                    "Неизвестно",
                                )
                            )


                            author_role = (
                                visit_comment.get(
                                    "author_role",
                                    "",
                                )
                            )


                            comment_text = (
                                visit_comment.get(
                                    "comment",
                                    "",
                                )
                            )


                            created_at = (
                                visit_comment.get(
                                    "created_at",
                                    "",
                                )
                            )


                            if author_role == "supervisor":

                                st.markdown(
                                    f"👩‍💼 **Супервайзер — {author}**"
                                )

                            else:

                                st.markdown(
                                    f"👤 **Мерчендайзер — {author}**"
                                )


                            st.write(
                                comment_text
                            )


                            if created_at:

                                st.caption(
                                    f"🕒 {created_at}"
                                )


                            st.divider()


                    else:

                        st.caption(
                            "Комментариев пока нет."
                        )


                    new_discussion_comment = (
                        st.text_area(
                            "Ответить в обсуждении",
                            placeholder=(
                                "Напишите ответ "
                                "супервайзеру..."
                            ),
                            key=(
                                f"worker_discussion_comment_"
                                f"{visit['id']}"
                            ),
                        )
                    )


                    if st.button(
                        "💬 Отправить ответ",
                        key=(
                            f"send_worker_discussion_comment_"
                            f"{visit['id']}"
                        ),
                        type="primary",
                        use_container_width=True,
                    ):

                        if not new_discussion_comment.strip():

                            st.warning(
                                "Введите комментарий."
                            )

                        else:

                            try:

                                create_visit_comment(
                                    visit["id"],
                                    worker,
                                    "worker",
                                    new_discussion_comment,
                                )

                                st.rerun()


                            except Exception as error:

                                st.error(
                                    f"Ошибка отправки "
                                    f"комментария: {error}"
                                )


                except Exception as error:

                    st.warning(
                        f"Не удалось загрузить "
                        f"комментарии: {error}"
                    )


                # =============================================
                # ДАТА ПРОХОЖДЕНИЯ
                # =============================================

                if visit.get(
                    "completed_at"
                ):

                    completed_at = str(
                        visit["completed_at"]
                    )


                    visit_date_display = (
                        completed_at[:10]
                    )


                    st.divider()


                    st.caption(
                        f"📅 Дата прохождения: "
                        f"{visit_date_display}"
                    )


                # =============================================
                # СБРОС
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
)


progress = (
    completed_points / total_points
    if total_points
    else 0
)


st.progress(
    progress
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "Всего ТТ",
    total_points,
)


col2.metric(
    "Пройдено",
    completed_points,
)


col3.metric(
    "Осталось",
    total_points - completed_points,
)
