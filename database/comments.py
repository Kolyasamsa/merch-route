from config import supabase


# =========================================================
# ПОЛУЧЕНИЕ КОММЕНТАРИЕВ К ПРОХОЖДЕНИЮ
# =========================================================

def get_visit_comments(
    visit_id,
):

    response = (

        supabase
        .table(
            "visit_comments"
        )
        .select(
            "*"
        )
        .eq(
            "visit_id",
            visit_id,
        )
        .order(
            "created_at",
            desc=False,
        )
        .execute()
    )

    return response.data


# =========================================================
# ДОБАВЛЕНИЕ КОММЕНТАРИЯ
# =========================================================

def create_visit_comment(
    visit_id,
    author,
    author_role,
    comment,
):

    comment = comment.strip()

    if not comment:

        return None

    response = (

        supabase
        .table(
            "visit_comments"
        )
        .insert(

            {

                "visit_id": visit_id,

                "author": author,

                "author_role": author_role,

                "comment": comment,

                "is_read": False,

            }

        )
        .execute()
    )

    return response.data


# =========================================================
# НЕПРОЧИТАННЫЕ КОММЕНТАРИИ ДЛЯ МЕРЧЕНДАЙЗЕРА
# =========================================================

def get_unread_comments_for_worker(
    worker,
):

    response = (

        supabase
        .table(
            "visit_comments"
        )
        .select(
            """
            *,
            point_visits!inner(
                id,
                visit_date,
                worker,
                weekday,
                route,
                shop,
                address
            )
            """
        )
        .eq(
            "author_role",
            "supervisor",
        )
        .eq(
            "is_read",
            False,
        )
        .eq(
            "point_visits.worker",
            worker,
        )
        .order(
            "created_at",
            desc=True,
        )
        .execute()
    )

    return response.data


# =========================================================
# НЕПРОЧИТАННЫЕ КОММЕНТАРИИ ДЛЯ СУПЕРВАЙЗЕРА
# =========================================================

def get_unread_comments_for_supervisor():

    response = (

        supabase
        .table(
            "visit_comments"
        )
        .select(
            """
            *,
            point_visits!inner(
                id,
                visit_date,
                worker,
                weekday,
                route,
                shop,
                address
            )
            """
        )
        .eq(
            "author_role",
            "worker",
        )
        .eq(
            "is_read",
            False,
        )
        .order(
            "created_at",
            desc=True,
        )
        .execute()
    )

    return response.data


# =========================================================
# ОТМЕТИТЬ КОММЕНТАРИЙ КАК ПРОЧИТАННЫЙ
# =========================================================

def mark_comment_as_read(
    comment_id,
):

    response = (

        supabase
        .table(
            "visit_comments"
        )
        .update(

            {
                "is_read": True,
            }

        )
        .eq(
            "id",
            comment_id,
        )
        .execute()
    )

    return response.data


    return response.data
