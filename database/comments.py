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

            }

        )
        .execute()
    )


    return response.data
