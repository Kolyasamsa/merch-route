import streamlit as st
from supabase import create_client


EXCEL_FILE = "routes.xlsx"

STORAGE_BUCKET = "point-photos"


DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
]


SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)
