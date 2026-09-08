from datetime import datetime

import streamlit as st

from config import supabase


# =========================================================
# ПОЛУЧЕНИЕ ПРОЙДЕННЫХ ТТ ЗА ДЕНЬ
# =========================================================

@st.cache_data(ttl=10)
def get_completed_visits(

    visit_date,
    worker,

):

    response = (

        supabase
        .table(
            "point_visits"
        )
        .select("*")
        .eq(
            "visit_date",
            visit_date,
        )
        .eq(
            "worker",
            worker,
        )
        .execute()

    )


    return response.data


# =========================================================
# СОЗДАНИЕ ПРОХОЖДЕНИЯ ТТ
# =========================================================

def create_visit(

    visit_date,
    worker,
    weekday,
    route,
    shop,
    address,
    comment,

):

    data = {

        "visit_date": visit_date,

        "worker": worker,

        "weekday": weekday,

        "route": route,

        "shop": shop,

        "address": address,

        "completed": True,

        "comment": comment,

        "completed_at": (
            datetime.now()
            .isoformat()
        ),

    }


    response = (

        supabase
        .table(
            "point_visits"
        )
        .insert(
            data
        )
        .execute()

    )


    if not response.data:

        raise RuntimeError(

            "Не удалось создать запись "
            "о прохождении ТТ."

        )


    clear_visits_cache()


    return response.data[0]


# =========================================================
# РЕДАКТИРОВАНИЕ КОММЕНТАРИЯ
# =========================================================

def update_visit_comment(

    visit_id,
    comment,

):

    response = (

        supabase
        .table(
            "point_visits"
        )
        .update(

            {
                "comment": comment,
            }

        )
        .eq(
            "id",
            str(visit_id),
        )
        .execute()

    )


    if not response.data:

        raise RuntimeError(

            "Комментарий "
            "не был обновлён."

        )


    clear_visits_cache()


    return response.data[0]


# =========================================================
# УДАЛЕНИЕ ПРОХОЖДЕНИЯ
# =========================================================

def delete_visit(
    visit_id,
):

    (

        supabase
        .table(
            "point_visits"
        )
        .delete()
        .eq(
            "id",
            str(visit_id),
        )
        .execute()

    )


    clear_visits_cache()


# =========================================================
# ПОЛУЧЕНИЕ ПРОЙДЕННЫХ ТТ ЗА ПЕРИОД
# =========================================================

@st.cache_data(ttl=30)
def get_completed_visits_for_period(

    start_date,
    end_date,

):

    response = (

        supabase
        .table(
            "point_visits"
        )
        .select(

            "worker, visit_date"

        )
        .gte(

            "visit_date",
            start_date,

        )
        .lte(

            "visit_date",
            end_date,

        )
        .eq(

            "completed",
            True,

        )
        .execute()

    )


    return response.data


# =========================================================
# ОЧИСТКА КЭША ПРОХОЖДЕНИЙ
# =========================================================

def clear_visits_cache():

    get_completed_visits.clear()

    get_completed_visits_for_period.clear()
