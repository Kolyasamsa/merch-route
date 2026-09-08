import uuid

from io import BytesIO

import streamlit as st

from PIL import (
    Image,
    ImageOps,
)

from config import (
    supabase,
    STORAGE_BUCKET,
)


# =========================================================
# ПОЛУЧЕНИЕ ФОТОГРАФИЙ ТТ
# =========================================================

@st.cache_data(ttl=10)
def get_visit_photos(

    visit_id,

):

    response = (

        supabase
        .table(
            "point_photos"
        )
        .select("*")
        .eq(

            "visit_id",
            str(visit_id),

        )
        .order(
            "created_at"
        )
        .execute()

    )


    return response.data


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
    # ИСПРАВЛЯЕМ ОРИЕНТАЦИЮ
    # -----------------------------------------------------

    image = ImageOps.exif_transpose(
        image
    )


    # -----------------------------------------------------
    # RGB
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
    # УМЕНЬШЕНИЕ РАЗРЕШЕНИЯ
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
    # СОХРАНЕНИЕ В ПАМЯТЬ
    # -----------------------------------------------------

    image_buffer = BytesIO()


    image.save(

        image_buffer,

        format="JPEG",

        quality=85,

        optimize=True,

    )


    image_bytes = (

        image_buffer
        .getvalue()

    )


    # -----------------------------------------------------
    # ИМЯ ФАЙЛА
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
    # ЗАГРУЗКА В STORAGE
    # -----------------------------------------------------

    supabase.storage.from_(

        STORAGE_BUCKET

    ).upload(

        path=file_path,

        file=image_bytes,

        file_options={

            "content-type":
                "image/jpeg",

        },

    )


    # -----------------------------------------------------
    # PUBLIC URL
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
    # СОХРАНЯЕМ В БАЗУ
    # -----------------------------------------------------

    photo_data = {

        "visit_id":
            str(visit_id),

        "file_path":
            file_path,

        "public_url":
            public_url,

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


    clear_photos_cache()


    return photo_data


# =========================================================
# ЗАГРУЗКА НЕСКОЛЬКИХ ФОТО
# =========================================================

def upload_visit_photos(

    files,
    visit_id,

):

    if not files:

        return []


    uploaded = []


    for file in files:


        photo = (

            upload_visit_photo(

                file,

                visit_id,

            )

        )


        uploaded.append(
            photo
        )


    return uploaded


# =========================================================
# ЗАМЕНА ФОТОГРАФИЙ
# =========================================================

def replace_visit_photos(

    files,
    visit_id,

):

    # Получаем старые фотографии

    photos_response = (

        supabase
        .table(

            "point_photos"

        )
        .select("*")
        .eq(

            "visit_id",

            str(visit_id),

        )
        .execute()

    )


    old_photos = (

        photos_response.data

        or []

    )


    # Пути файлов

    old_file_paths = [

        photo[
            "file_path"
        ]

        for photo

        in old_photos

    ]


    # Удаляем из Storage

    if old_file_paths:


        supabase.storage.from_(

            STORAGE_BUCKET

        ).remove(

            old_file_paths

        )


    # Удаляем записи из БД

    (

        supabase
        .table(

            "point_photos"

        )
        .delete()
        .eq(

            "visit_id",

            str(visit_id),

        )
        .execute()

    )


    # Загружаем новые

    uploaded_photos = (

        upload_visit_photos(

            files,

            visit_id,

        )

    )


    clear_photos_cache()


    return uploaded_photos


# =========================================================
# УДАЛЕНИЕ ВСЕХ ФОТО ТТ
# =========================================================

def delete_visit_photos(

    visit_id,

):

    photos_response = (

        supabase
        .table(

            "point_photos"

        )
        .select("*")
        .eq(

            "visit_id",

            str(visit_id),

        )
        .execute()

    )


    photos = (

        photos_response.data

        or []

    )


    file_paths = [

        photo[
            "file_path"
        ]

        for photo

        in photos

    ]


    # Удаляем файлы

    if file_paths:


        supabase.storage.from_(

            STORAGE_BUCKET

        ).remove(

            file_paths

        )


    # Удаляем записи

    (

        supabase
        .table(

            "point_photos"

        )
        .delete()
        .eq(

            "visit_id",

            str(visit_id),

        )
        .execute()

    )


    clear_photos_cache()


# =========================================================
# ОЧИСТКА КЭША
# =========================================================

def clear_photos_cache():

    get_visit_photos.clear()
