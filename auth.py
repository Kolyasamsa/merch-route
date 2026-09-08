import streamlit as st


# =========================================================
# ПОИСК МЕРЧЕНДАЙЗЕРА ПО ПАРОЛЮ
# =========================================================

def get_worker_by_password(
    password,
):

    workers = st.secrets.get(
        "workers",
        {},
    )

    for worker, worker_password in workers.items():

        if password == worker_password:

            return worker

    return None


# =========================================================
# ПОИСК СУПЕРВАЙЗЕРА ПО ПАРОЛЮ
# =========================================================

def get_supervisor_by_password(
    password,
):

    supervisors = st.secrets.get(
        "supervisors",
        {},
    )

    for supervisor, supervisor_password in supervisors.items():

        if password == supervisor_password:

            return supervisor

    return None


# =========================================================
# АВТОРИЗАЦИЯ
# =========================================================

def login():

    # -----------------------------------------------------
    # ПРОВЕРКА УЖЕ АВТОРИЗОВАННОГО ПОЛЬЗОВАТЕЛЯ
    # -----------------------------------------------------

    if (
        "user_name" in st.session_state
        and
        "user_role" in st.session_state
    ):

        return (
            st.session_state["user_name"],
            st.session_state["user_role"],
        )


    # -----------------------------------------------------
    # ЭКРАН ВХОДА
    # -----------------------------------------------------

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

            return None, None


        # -------------------------------------------------
        # СНАЧАЛА ИЩЕМ МЕРЧЕНДАЙЗЕРА
        # -------------------------------------------------

        worker = (
            get_worker_by_password(
                password
            )
        )


        if worker:

            st.session_state[
                "user_name"
            ] = worker

            st.session_state[
                "user_role"
            ] = "worker"

            st.rerun()


        # -------------------------------------------------
        # ИЩЕМ СУПЕРВАЙЗЕРА
        # -------------------------------------------------

        supervisor = (
            get_supervisor_by_password(
                password
            )
        )


        if supervisor:

            st.session_state[
                "user_name"
            ] = supervisor

            st.session_state[
                "user_role"
            ] = "supervisor"

            st.rerun()


        st.error(
            "Неверный пароль."
        )


    return None, None


# =========================================================
# ВЫХОД
# =========================================================

def logout():

    st.session_state.pop(
        "user_name",
        None,
    )

    st.session_state.pop(
        "user_role",
        None,
    )

    st.rerun()
