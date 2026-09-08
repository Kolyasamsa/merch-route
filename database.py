import uuid
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps

from config import (
    supabase,
    STORAGE_BUCKET,
)


# =========================================================
# ПОЛУЧЕНИЕ ПРОЙДЕННЫХ ТТ
# =========================================================

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


# =========================================================
# ПОЛУЧЕНИЕ ФОТОГРАФИЙ ТТ
# =========================================================

@st.cache_data(ttl=10)
def get_visit_photos(
    visit_id,
):

    response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq("visit_id", str(visit_id))
        .order("created_at")
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


# =========================================================
# ЗАГРУЗКА И СЖАТИЕ ОДНОЙ ФОТОГРАФИИ
# =========================================================

def upload_visit_photo(
    uploaded_file,
    visit_id,
):

    # -----------------------------------------------------
    # ОТКРЫВАЕМ ИЗОБРАЖЕНИЕ
    # -----------------------------------------------------

    image = Image.open(
        BytesIO(
            uploaded_file.getvalue()
        )
    )


    # -----------------------------------------------------
    # ИСПРАВЛЯЕМ ОРИЕНТАЦИЮ ФОТО
    # -----------------------------------------------------

    image = ImageOps.exif_transpose(
        image
    )


    # -----------------------------------------------------
    # ПРИВОДИМ ИЗОБРАЖЕНИЕ К RGB
    # -----------------------------------------------------

    if image.mode != "RGB":

        if image.mode == "RGBA":

            background = Image.new(
                "RGB",
                image.size,
                "white",
            )

            background.paste(
                image,
                mask=image.getchannel(
                    "A"
                ),
            )

            image = background

        else:

            image = image.convert(
                "RGB"
            )


    # -----------------------------------------------------
    # УМЕНЬШАЕМ РАЗМЕР
    # -----------------------------------------------------

    max_size = (
        2560,
        2560,
    )


    image.thumbnail(
        max_size,
        Image.Resampling.LANCZOS,
    )


    # -----------------------------------------------------
    # СОХРАНЯЕМ СЖАТОЕ ФОТО В ПАМЯТЬ
    # -----------------------------------------------------

    image_buffer = BytesIO()


    image.save(

        image_buffer,

        format="JPEG",

        quality=85,

        optimize=True,
    )


    image_bytes = (
        image_buffer.getvalue()
    )


    # -----------------------------------------------------
    # СОЗДАЁМ НОВОЕ ИМЯ ФАЙЛА
    # -----------------------------------------------------

    file_name = (
        f"{uuid.uuid4()}.jpg"
    )


    file_path = (
        f"visits/"
        f"{visit_id}/"
        f"{file_name}"
    )


    # -----------------------------------------------------
    # ЗАГРУЖАЕМ В SUPABASE STORAGE
    # -----------------------------------------------------

    supabase.storage.from_(
        STORAGE_BUCKET
    ).upload(

        path=file_path,

        file=image_bytes,

        file_options={
            "content-type": "image/jpeg",
        },
    )


    # -----------------------------------------------------
    # ПОЛУЧАЕМ PUBLIC URL
    # -----------------------------------------------------

    public_url = (
        supabase
        .storage
        .from_(
            STORAGE_BUCKET
        )
        .get_public_url(
            file_path
        )
    )


    # -----------------------------------------------------
    # СОХРАНЯЕМ ИНФОРМАЦИЮ О ФОТО В БАЗУ
    # -----------------------------------------------------

    photo_data = {
        "visit_id": str(
            visit_id
        ),
        "file_path": file_path,
        "public_url": public_url,
    }


    (
        supabase
        .table(
            "point_photos"
        )
        .insert(
            photo_data
        )
        .execute()
    )


    return photo_data


# =========================================================
# ЗАГРУЗКА НЕСКОЛЬКИХ ФОТОГРАФИЙ
# =========================================================

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

        uploaded.append(
            photo
        )

    return uploaded


# =========================================================
# ЗАМЕНА ФОТОГРАФИЙ ТТ
# =========================================================

def replace_visit_photos(
    files,
    visit_id,
):

    # Получаем текущие фотографии
    photos_response = (
        supabase
        .table("point_photos")
        .select("*")
        .eq("visit_id", str(visit_id))
        .execute()
    )

    old_photos = (
        photos_response.data
        or []
    )


    # Получаем пути старых файлов
    old_file_paths = [

        photo["file_path"]

        for photo in old_photos
    ]


    # Удаляем старые файлы из Storage
    if old_file_paths:

        supabase.storage.from_(
            STORAGE_BUCKET
        ).remove(
            old_file_paths
        )


    # Удаляем старые записи из базы
    (
        supabase
        .table("point_photos")
        .delete()
        .eq(
            "visit_id",
            str(visit_id),
        )
        .execute()
    )


    # Загружаем новые фотографии
    uploaded_photos = (
        upload_visit_photos(
            files,
            visit_id,
        )
    )


    # Очищаем кэш
    clear_database_cache()


    return uploaded_photos


# =========================================================
# СБРОС ПРОХОЖДЕНИЯ ТТ
# =========================================================

def reset_visit(
    visit_id,
):

    # Получаем фотографии ТТ
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


    # Получаем пути файлов
    file_paths = [

        photo["file_path"]

        for photo in photos
    ]


    # Удаляем файлы из Storage
    if file_paths:

        supabase.storage.from_(
            STORAGE_BUCKET
        ).remove(
            file_paths
        )


    # Удаляем записи о фотографиях
    (
        supabase
        .table("point_photos")
        .delete()
        .eq(
            "visit_id",
            str(visit_id),
        )
        .execute()
    )


    # Удаляем прохождение ТТ
    (
        supabase
        .table("point_visits")
        .delete()
        .eq(
            "id",
            str(visit_id),
        )
        .execute()
    )


    clear_database_cache()


# =========================================================
# РЕДАКТИРОВАНИЕ КОММЕНТАРИЯ
# =========================================================

def update_visit_comment(
    visit_id,
    comment,
):

    response = (
        supabase
        .table("point_visits")
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
            "Комментарий не был обновлён."
        )


    clear_database_cache()


    return response.data[0]


# =========================================================
# ОЧИСТКА КЭША
# =========================================================

def clear_database_cache():

    get_completed_visits.clear()

    get_visit_photos.clear()
