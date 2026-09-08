import os

import pandas as pd
import streamlit as st

from config import EXCEL_FILE, DAYS


REQUIRED_COLUMNS = [
    "Мерчендайзер",
    "Маршрут",
    "День",
    "Магазин",
    "Адрес",
]


@st.cache_data
def load_routes():

    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(
            f"Файл {EXCEL_FILE} не найден."
        )

    df = pd.read_excel(EXCEL_FILE)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "В Excel отсутствуют столбцы: "
            + ", ".join(missing_columns)
        )

    for column in REQUIRED_COLUMNS:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df


def get_workers(df):

    return sorted(
        df["Мерчендайзер"]
        .dropna()
        .unique()
        .tolist()
    )


def get_worker_data(df, worker):

    return df[
        df["Мерчендайзер"] == worker
    ].copy()


def get_available_days(worker_data):

    existing_days = (
        worker_data["День"]
        .unique()
        .tolist()
    )

    return [
        day
        for day in DAYS
        if day in existing_days
    ]


def get_routes_for_day(worker_data, day):

    day_data = worker_data[
        worker_data["День"] == day
    ].copy()

    routes = (
        day_data["Маршрут"]
        .dropna()
        .unique()
        .tolist()
    )

    return day_data, routes
