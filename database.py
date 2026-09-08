import uuid
from datetime import datetime

import streamlit as st

from config import (
    supabase,
    STORAGE_BUCKET,
)


@st.cache_data(ttl=10)
def get_completed_visits(
    visit_date,
    worker,
):

    response = (
        supabase
        .table("point_visits")
        .select("*")
        .eq("visit_date", visit_date)
        .eq("worker", worker)
        .execute()
    )

    return response.data


@st.cache_data(ttl=10)
def get_visit_photos(visit_id):

    response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq("visit_id", str(visit_id))
        .order("created_at")
        .execute()
    )

    return response.data


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
        "completed_at": datetime.now().isoformat(),
    }

    response = (
        supabase
        .table("point_visits")
        .insert(data)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Не удалось создать запись о прохождении ТТ."
        )

    return response.data[0]


def upload_visit_photo(
    uploaded_file,
    visit_id,
):

    extension = (
        uploaded_file.name
        .rsplit(".", 1)[-1]
        .lower()
        if "." in uploaded_file.name
        else "jpg"
    )

    file_name = (
        f"{uuid.uuid4()}.{extension}"
    )

    file_path = (
        f"visits/{visit_id}/{file_name}"
    )

    supabase.storage.from_(
        STORAGE_BUCKET
    ).upload(
        path=file_path,
        file=uploaded_file.getvalue(),
        file_options={
            "content-type": uploaded_file.type,
        },
    )

    public_url = (
        supabase
        .storage
        .from_(STORAGE_BUCKET)
        .get_public_url(file_path)
    )

    photo_data = {
        "visit_id": str(visit_id),
        "file_path": file_path,
        "public_url": public_url,
    }

    (
        supabase
        .table("point_photos")
        .insert(photo_data)
        .execute()
    )

    return photo_data


def upload_visit_photos(
    files,
    visit_id,
):

    if not files:
        return []

    uploaded = []

    for file in files:

        photo = upload_visit_photo(
            file,
            visit_id,
        )

        uploaded.append(photo)

    return uploaded


def reset_visit(
    visit_id,
):

    photos_response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq("visit_id", str(visit_id))
        .execute()
    )

    photos = (
        photos_response.data
        or []
    )

    file_paths = [
        photo["file_path"]
        for photo in photos
    ]

    if file_paths:

        supabase.storage.from_(
            STORAGE_BUCKET
        ).remove(file_paths)

    (
        supabase
        .table("point_photos")
        .delete()
        .eq("visit_id", str(visit_id))
        .execute()
    )

    (
        supabase
        .table("point_visits")
        .delete()
        .eq("id", str(visit_id))
        .execute()
    )

    clear_database_cache()


def clear_database_cache():

    get_completed_visits.clear()
    get_visit_photos.clear()
