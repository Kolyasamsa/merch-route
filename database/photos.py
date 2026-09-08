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

# ПОЛУЧЕНИЕ ФОТОГРАФИЙ

# =========================================================

@st.cache_data(ttl=10)
def get_visit_photos(
visit_id,
):

```
response = (
    supabase
    .table("point_photos")
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
```

# =========================================================

# ЗАГРУЗКА И СЖАТИЕ ОДНОЙ ФОТОГРАФИИ

# =========================================================

def upload_visit_photo(
uploaded_file,
visit_id,
):

```
# -----------------------------------------------------
# ОТКРЫВАЕМ
# -----------------------------------------------------

image = Image.open(
    BytesIO(
        uploaded_file.getvalue()
    )
)


# -----------------------------------------------------
# ИСПРАВЛЯЕМ ORIENTATION
# -----------------------------------------------------

image = (
    ImageOps.exif_transpose(
        image
    )
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
# УМЕНЬШЕНИЕ РАЗМЕРА
# -----------------------------------------------------

image.thumbnail(

    (
        2560,
        2560,
    ),

    Image.Resampling.LANCZOS,
)


# -----------------------------------------------------
# СЖАТИЕ
# -----------------------------------------------------

image_buffer = (
    BytesIO()
)


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
# ПУТЬ
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
# STORAGE
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
# БАЗА
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
    .table("point_photos")
    .insert(
        photo_data
    )
    .execute()
)


get_visit_photos.clear()


return photo_data
```

# =========================================================

# ЗАГРУЗКА НЕСКОЛЬКИХ ФОТО

# =========================================================

def upload_visit_photos(
files,
visit_id,
):

```
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


get_visit_photos.clear()


return uploaded
```

# =========================================================

# ЗАМЕНА ФОТО

# =========================================================

def replace_visit_photos(
files,
visit_id,
):

```
# -----------------------------------------------------
# ПОЛУЧАЕМ СТАРЫЕ
# -----------------------------------------------------

response = (
    supabase
    .table("point_photos")
    .select("*")
    .eq(
        "visit_id",
        str(visit_id),
    )
    .execute()
)


old_photos = (
    response.data
    or []
)


# -----------------------------------------------------
# УДАЛЯЕМ ФАЙЛЫ
# -----------------------------------------------------

old_file_paths = [

    photo["file_path"]

    for photo
    in old_photos
]


if old_file_paths:

    supabase.storage.from_(
        STORAGE_BUCKET
    ).remove(
        old_file_paths
    )


# -----------------------------------------------------
# УДАЛЯЕМ ЗАПИСИ
# -----------------------------------------------------

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


# -----------------------------------------------------
# ЗАГРУЖАЕМ НОВЫЕ
# -----------------------------------------------------

uploaded_photos = (
    upload_visit_photos(
        files,
        visit_id,
    )
)


get_visit_photos.clear()


return uploaded_photos
```

# =========================================================

# УДАЛЕНИЕ ВСЕХ ФОТО ТТ

# =========================================================

def delete_visit_photos(
visit_id,
):

```
response = (
    supabase
    .table("point_photos")
    .select("*")
    .eq(
        "visit_id",
        str(visit_id),
    )
    .execute()
)


photos = (
    response.data
    or []
)


file_paths = [

    photo["file_path"]

    for photo
    in photos
]


if file_paths:

    supabase.storage.from_(
        STORAGE_BUCKET
    ).remove(
        file_paths
    )


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


get_visit_photos.clear()
```
