import pandas as pd

import streamlit as st


# =========================================================
# ЗАГРУЗКА МАРШРУТОВ
# =========================================================

@st.cache_data
def load_routes():

    df = pd.read_csv(
        "routes.csv"
    )

    return df


# =========================================================
# ПОЛУЧЕНИЕ ВСЕХ МЕРЧЕНДАЙЗЕРОВ
# =========================================================

def get_workers(
    df,
):

    workers = (

        df[
            "Мерчендайзер"
        ]
        .dropna()
        .unique()
        .tolist()

    )


    return sorted(
        workers
    )


# =========================================================
# ДАННЫЕ КОНКРЕТНОГО МЕРЧЕНДАЙЗЕРА
# =========================================================

def get_worker_data(

    df,
    worker,

):

    return df[

        df[
            "Мерчендайзер"
        ]
        == worker

    ].copy()


# =========================================================
# ДОСТУПНЫЕ ДНИ
# =========================================================

def get_available_days(
    worker_data,
):

    days = (

        worker_data[
            "День"
        ]
        .dropna()
        .unique()
        .tolist()

    )


    return days


# =========================================================
# МАРШРУТЫ НА КОНКРЕТНЫЙ ДЕНЬ
# =========================================================

def get_routes_for_day(

    worker_data,
    day,

):

    day_data = (

        worker_data[

            worker_data[
                "День"
            ]
            == day

        ]
        .copy()

    )


    routes = (

        day_data[
            "Маршрут"
        ]
        .dropna()
        .unique()
        .tolist()

    )


    return (
        day_data,
        routes,
    )
