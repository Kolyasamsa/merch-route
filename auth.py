import streamlit as st


def get_worker_by_password(password):
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


def login():
    """
    Показывает экран входа.

    Если пользователь уже вошёл —
    возвращает его имя.

    Если ещё не вошёл —
    показывает поле пароля.
    """

    # Проверяем, есть ли уже авторизованный пользователь
    if "worker" in st.session_state:

        return st.session_state["worker"]


    # Экран входа
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


        worker = get_worker_by_password(
            password
        )


        if worker:

            # Запоминаем вошедшего мерчендайзера
            st.session_state["worker"] = (
                worker
            )

            st.rerun()


        else:

            st.error(
                "Неверный пароль."
            )


    return None


def logout():
    """
    Выход из аккаунта.
    """

    st.session_state.pop(
        "worker",
        None,
    )

    st.rerun()
