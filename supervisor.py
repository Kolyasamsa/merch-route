from datetime import date
import calendar
from io import BytesIO

import pandas as pd
import streamlit as st
import re



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

    safe_prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", str(key_prefix))
    overlay_id = f"photo_overlay_{safe_prefix}"
    image_id = f"photo_full_{safe_prefix}"

    cards = []
    for index, photo in enumerate(photos):
        url = str(photo["public_url"])
        url_attr = html.escape(url, quote=True)
        url_js = json.dumps(url)
        cards.append(
            f'<button type="button" class="photo-card" '
            f'onclick="openPhoto_{safe_prefix}({html.escape(url_js, quote=True)})">'
            f'<img src="{url_attr}" loading="lazy" alt="Фото {index + 1}" />'
            f'</button>'
        )

    gallery = f"""
    <style>
      .photo-gallery-{safe_prefix} {{
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 10px;
          width: 100%;
          margin: 8px 0 14px;
      }}
      .photo-gallery-{safe_prefix} .photo-card {{
          padding: 0;
          border: 1px solid rgba(128,128,128,.22);
          background: rgba(128,128,128,.08);
          border-radius: 12px;
          overflow: hidden;
          cursor: pointer;
          width: 100%;
          aspect-ratio: 4 / 3;
          display: block;
      }}
      .photo-gallery-{safe_prefix} .photo-card img {{
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
      }}
      .photo-gallery-{safe_prefix} .photo-card:active {{
          opacity: .75;
      }}
      #{overlay_id} {{
          display: none;
          position: fixed;
          inset: 0;
          z-index: 999999;
          background: rgba(0,0,0,.90);
          align-items: center;
          justify-content: center;
          padding: 18px;
      }}
      #{overlay_id}.open {{
          display: flex;
      }}
      #{overlay_id} img {{
          max-width: 96vw;
          max-height: 92vh;
          width: auto;
          height: auto;
          object-fit: contain;
          border-radius: 8px;
      }}
      #{overlay_id} .photo-close {{
          position: fixed;
          top: 12px;
          right: 14px;
          width: 44px;
          height: 44px;
          border: 0;
          border-radius: 50%;
          background: rgba(255,255,255,.20);
          color: white;
          font-size: 30px;
          line-height: 1;
          cursor: pointer;
      }}
      @media (max-width: 700px) {{
          .photo-gallery-{safe_prefix} {{
              grid-template-columns: repeat(2, minmax(0, 1fr));
              gap: 8px;
          }}
          #{overlay_id} {{
              padding: 10px;
          }}
          #{overlay_id} img {{
              max-width: 98vw;
              max-height: 88vh;
          }}
      }}
    </style>

    <div class="photo-gallery-{safe_prefix}">
        {''.join(cards)}
    </div>

    <div id="{overlay_id}" onclick="closePhoto_{safe_prefix}(event)">
        <button type="button" class="photo-close"
                onclick="closePhoto_{safe_prefix}(event)">×</button>
        <img id="{image_id}" src="" alt="Увеличенное фото"
             onclick="event.stopPropagation()" />
    </div>

    <script>
      function openPhoto_{safe_prefix}(url) {{
          const overlay = document.getElementById("{overlay_id}");
          const image = document.getElementById("{image_id}");
          if (!overlay || !image) return;
          image.src = url;
          overlay.classList.add("open");
          document.body.style.overflow = "hidden";
      }}

      function closePhoto_{safe_prefix}(event) {{
          if (event) event.stopPropagation();
          const overlay = document.getElementById("{overlay_id}");
          const image = document.getElementById("{image_id}");
          if (!overlay || !image) return;
          overlay.classList.remove("open");
          image.src = "";
          document.body.style.overflow = "";
      }}
    </script>
    """

    st.html(gallery, unsafe_allow_javascript=True)


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
        width="stretch",
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
        width="stretch",
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
            width="stretch",
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

                                width="stretch",
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
