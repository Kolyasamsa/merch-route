from database.visits import (

    get_completed_visits,

    create_visit,

    update_visit_comment,

    delete_visit,

    get_completed_visits_for_period,

)


from database.photos import (

    get_visit_photos,

    upload_visit_photos,

    replace_visit_photos,

    delete_visit_photos,

)


# =========================================================
# СБРОС ПРОХОЖДЕНИЯ ТТ
# =========================================================

def reset_visit(
    visit_id,
):

    delete_visit_photos(
        visit_id
    )


    delete_visit(
        visit_id
    )


# =========================================================
# ОБЩАЯ ОЧИСТКА КЭША
# =========================================================

def clear_database_cache():

    from database.visits import (
        clear_visits_cache,
    )

    from database.photos import (
        clear_photos_cache,
    )


    clear_visits_cache()

    clear_photos_cache()
