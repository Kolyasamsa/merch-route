import streamlit as st


# =========================================================
# ПОИСК МЕРЧЕНДАЙЗЕРА ПО ПАРОЛЮ
# =========================================================

def get_worker_by_password(
    password,
):
    """
    Возвращает имя мерчендайзера,
    которому принадлежит введённый пароль.
    """

    workers = st.secrets.get(
        "workers",
        {},
    )

    for worker, worker_password in workers.items():

        if password == worker_password:

            return worker

    return None


# =========================================================
# ВХОД
# =========================================================

def login():
    """
    Показывает экран входа.

    Если пользователь уже авторизован,
    возвращает его имя.

    Если нет —
    показывает поле ввода пароля.
    """

    if "worker" in st.session_state:

        return st.session_state[
            "worker"
        ]


    st.title(
        "📍 Маршруты мерчендайзеров"
    )


    st.caption(
        "Введите свой пароль"
    )


    password = st.text_input(

        "🔐 Пароль",

        type="password",
    )


    if st.button(

        "Войти",

        type="primary",

        use_container_width=True,
    ):


        if not password:

            st.warning(
                "Введите пароль."
            )

            return None


        worker = (
            get_worker_by_password(
                password
            )
        )


        if worker:


            st.session_state[
                "worker"
            ] = worker


            st.rerun()


        else:

            st.error(
                "Неверный пароль."
            )


    return None


# =========================================================
# ВЫХОД
# =========================================================

def logout():

    st.session_state.pop(
        "worker",
        None,
    )

    st.rerun()
