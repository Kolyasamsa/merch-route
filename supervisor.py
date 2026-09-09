from datetime import date
import calendar
from io import BytesIO

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components



from config import DAYS

from routes import (
    get_workers,
    get_worker_data,
    get_available_days,
    get_routes_for_day,
)

from database import (
    get_completed_visits,
    get_visit_photos,
    get_completed_visits_for_period,
    get_visit_comments,
    create_visit_comment,
)

from utils import (
    MONTHS,
    get_point_key,
    get_dates_for_weekday,
    get_default_date,
)


def render_photo_grid(photos, key_prefix="photo"):
    if not photos:
        return

    import html

    cards = []
    for photo in photos:
        url = html.escape(photo["public_url"], quote=True)
        cards.append(
            f'<button class="photo-card" onclick="openPhoto(\'{url}\')">'
            f'<img src="{url}" loading="lazy" />'
            f'</button>'
        )

    gallery = """
    <style>
      * { box-sizing: border-box; }
      body { margin: 0; font-family: sans-serif; }
      .photo-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; width: 100%; }
      .photo-card { padding: 0; border: 0; background: transparent; border-radius: 12px; overflow: hidden; cursor: pointer; width: 100%; aspect-ratio: 4 / 3; }
      .photo-card img { width: 100%; height: 100%; object-fit: cover; display: block; }
      .photo-card:active { opacity: .8; }
      .overlay { display: none; position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,.88); align-items: center; justify-content: center; padding: 18px; }
      .overlay.open { display: flex; }
      .overlay img { max-width: 100%; max-height: 90vh; object-fit: contain; border-radius: 8px; }
      .close { position: fixed; top: 10px; right: 14px; width: 42px; height: 42px; border: 0; border-radius: 50%; background: rgba(255,255,255,.18); color: white; font-size: 28px; cursor: pointer; }
      @media (max-width: 700px) { .photo-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; } }
    </style>
    <div class="photo-grid">__CARDS__</div>
    <div class="overlay" id="photoOverlay" onclick="closePhoto(event)">
      <button class="close" onclick="closePhoto(event)">×</button>
      <img id="fullPhoto" src="" />
    </div>
    <script>
      function openPhoto(url) { document.getElementById('fullPhoto').src = url; document.getElementById('photoOverlay').classList.add('open'); }
      function closePhoto(e) { if (e) e.stopPropagation(); document.getElementById('photoOverlay').classList.remove('open'); document.getElementById('fullPhoto').src = ''; }
    </script>
    """.replace("__CARDS__", """ + ''.join(cards) + """ )

    rows = (len(photos) + 2) // 3
    mobile_rows = (len(photos) + 1) // 2
    height = max(170, rows * 180 + 20, mobile_rows * 150 + 20)
    components.html(gallery, height=height, scrolling=False)


def show_timesheet(df):

    st.subheader("📊 Табель прохождений")

    today = date.today()

    col_year, col_month = st.columns(2)

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
            key="timesheet_year",
        )

    with col_month:

        month_name = st.selectbox(
            "📅 Месяц",
            MONTHS,
            index=today.month - 1,
            key="timesheet_month",
        )

    month = MONTHS.index(month_name) + 1

    days_in_month = calendar.monthrange(
        year,
        month,
    )[1]

    start_date = date(
        year,
        month,
        1,
    ).strftime("%Y-%m-%d")

    end_date = date(
        year,
        month,
        days_in_month,
    ).strftime("%Y-%m-%d")

    try:

        visits = get_completed_visits_for_period(
            start_date,
            end_date,
        )

    except Exception as error:

        st.error(
            f"Ошибка загрузки табеля: {error}"
        )

        return

    workers = get_workers(df)

    visit_counts = {}

    for visit in visits:

        worker = visit["worker"]

        visit_date = visit["visit_date"]

        key = (
            worker,
            visit_date,
        )

        visit_counts[key] = (
            visit_counts.get(
                key,
                0,
            )
            + 1
        )

    table_data = []

    for worker in workers:

        row = {
            "Мерчендайзер": worker,
        }

        total = 0

        for day_number in range(
            1,
            days_in_month + 1,
        ):

            current_date = date(
                year,
                month,
                day_number,
            ).strftime("%Y-%m-%d")

            completed_count = visit_counts.get(
                (
                    worker,
                    current_date,
                ),
                0,
            )

            column_name = (
                f"{day_number:02d}."
                f"{month_name[:3]}"
            )

            row[column_name] = completed_count

            total += completed_count

        row["Итого"] = total

        table_data.append(row)

    timesheet_df = pd.DataFrame(
        table_data
    )

    st.dataframe(
        timesheet_df,
        use_container_width=True,
        hide_index=True,
    )

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl",
    ) as writer:

        timesheet_df.to_excel(
            writer,
            index=False,
            sheet_name="Табель",
        )

    excel_data = excel_buffer.getvalue()

    st.download_button(
        label="⬇️ Скачать табель Excel",
        data=excel_data,
        file_name=(
            f"Табель_{month_name}_{year}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )


def show_supervisor_dashboard(
    df,
    supervisor,
    logout,
):


    col_title, col_logout = st.columns(
        [4, 1]
    )

    with col_title:

        st.title(
            "👩‍💼 Панель супервайзера"
        )

        st.caption(
            f"👤 Супервайзер: {supervisor}"
        )

    with col_logout:

        st.write("")

        if st.button(
            "🚪 Выйти",
            use_container_width=True,
        ):

            logout()

    tab_routes, tab_timesheet = st.tabs(
        [
            "📍 Просмотр маршрутов",
            "📊 Табель",
        ]
    )

    with tab_routes:

        workers = get_workers(df)

        selected_worker = st.selectbox(
            "👤 Мерчендайзер",
            workers,
            key="supervisor_worker",
        )

        worker_data = get_worker_data(
            df,
            selected_worker,
        )

        available_days = get_available_days(
            worker_data
        )

        today = date.today()

        today_day_index = today.weekday()

        default_day = (
            DAYS[today_day_index]

            if (
                today_day_index < len(DAYS)
                and DAYS[today_day_index]
                in available_days
            )

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
            key="supervisor_day",
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
            key="supervisor_year",
        )

        month_name = st.selectbox(
            "📅 Месяц",
            MONTHS,
            index=today.month - 1,
            key="supervisor_month",
        )

        month = (
            MONTHS.index(
                month_name
            )
            + 1
        )

        available_dates = get_dates_for_weekday(
            year,
            month,
            day,
        )

        default_date = get_default_date(
            available_dates
        )

        selected_date = st.selectbox(
            "📆 Дата маршрута",
            available_dates,
            index=available_dates.index(
                default_date
            ),
            format_func=lambda value:
                value.strftime(
                    "%d.%m.%Y"
                ),
            key="supervisor_date",
        )

        selected_date_string = (
            selected_date.strftime(
                "%Y-%m-%d"
            )
        )

        day_data, routes = get_routes_for_day(
            worker_data,
            day,
        )

        try:

            visits = get_completed_visits(
                selected_date_string,
                selected_worker,
            )

        except Exception as error:

            st.error(
                f"Ошибка загрузки прохождений: "
                f"{error}"
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
            f"👤 {selected_worker}"
        )

        st.write(
            f"📅 **{day}, "
            f"{selected_date.strftime('%d.%m.%Y')}**"
        )

        total_points = len(
            day_data
        )

        completed_points = sum(

            get_point_key(
                selected_worker,
                day,
                point["Маршрут"],
                point["Магазин"],
                point["Адрес"],
            )

            in completed_visits

            for _, point
            in day_data.iterrows()
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
            total_points
            - completed_points,
        )

        st.progress(
            completed_points / total_points
            if total_points
            else 0
        )

        for route in routes:

            route_data = day_data[
                day_data["Маршрут"]
                == route
            ]

            total_route_points = len(
                route_data
            )

            completed_route_points = sum(

                get_point_key(
                    selected_worker,
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
                completed_route_points
                / total_route_points
                if total_route_points
                else 0
            )

            st.caption(
                f"Пройдено: "
                f"{completed_route_points}"
                f" / "
                f"{total_route_points}"
            )

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
                    selected_worker,
                    day,
                    route,
                    shop,
                    address,
                )

                visit = completed_visits.get(
                    point_key
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
                        f"🏪 **Магазин:** "
                        f"{shop}"
                    )

                    st.write(
                        f"📍 **Адрес:** "
                        f"{address}"
                    )

                    if not is_completed:

                        st.error(
                            "🔴 ТТ не пройдена"
                        )

                    else:

                        st.success(
                            "🟢 ТТ пройдена"
                        )

                        if visit.get(
                            "completed_at"
                        ):

                            st.write(
                                f"🕒 **Время:** "
                                f"{visit['completed_at']}"
                            )

                        comment = visit.get(
                            "comment",
                            "",
                        )

                        st.divider()

                        st.write(
                            "💬 **Комментарий мерчендайзера:**"
                        )

                        if comment:

                            st.write(
                                comment
                            )

                        else:

                            st.caption(
                                "Комментарий отсутствует"
                            )

                        st.divider()

                        try:

                            photos = (
                                get_visit_photos(
                                    visit["id"]
                                )
                            )

                            if photos:

                                st.write(
                                    "📷 **Фотографии:**"
                                )

                                render_photo_grid(
                                    photos,
                                    f"supervisor_{visit['id']}",
                                )

                            else:

                                st.info(
                                    "Фотографии отсутствуют."
                                )

                        except Exception as error:

                            st.warning(
                                f"Не удалось загрузить "
                                f"фотографии: {error}"
                            )

                        st.divider()

                        st.subheader(
                            "💬 Обсуждение ТТ"
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

                                    if (
                                        author_role
                                        == "supervisor"
                                    ):

                                        role_text = (
                                            "👩‍💼 Супервайзер"
                                        )

                                    else:

                                        role_text = (
                                            "👤 Мерчендайзер"
                                        )

                                    st.markdown(
                                        f"**{role_text}: "
                                        f"{author}**"
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

                            new_comment = st.text_area(

                                "Написать комментарий",

                                placeholder=(
                                    "Например: торты нужно было "
                                    "переставить на уровень глаз..."
                                ),

                                key=(
                                    f"supervisor_comment_"
                                    f"{visit['id']}"
                                ),
                            )

                            if st.button(

                                "💬 Отправить комментарий",

                                key=(
                                    f"send_supervisor_comment_"
                                    f"{visit['id']}"
                                ),

                                type="primary",

                                use_container_width=True,
                            ):

                                if not new_comment.strip():

                                    st.warning(
                                        "Введите комментарий."
                                    )

                                else:

                                    try:

                                        create_visit_comment(

                                            visit["id"],

                                            supervisor,

                                            "supervisor",

                                            new_comment,
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

    with tab_timesheet:

        show_timesheet(df)
