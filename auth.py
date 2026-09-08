import streamlit as st


def get_worker_by_password(password):

    workers = st.secrets.get(
        "workers",
        {},
    )

    for worker, worker_password in workers.items():

        if password == worker_password:

            return worker

    return None


def login():

    # Пользователь уже вошёл
    if st.session_state.get("worker"):

        return st.session_state["worker"]


    st.title(
        "📍 Маршруты мерчендайзеров"
    )

    st.write(
        "Войдите, чтобы открыть свои маршруты."
    )


    password = st.text_input(
        "🔐 Пароль",
        type="password",
        key="login_password",
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

            st.session_state["worker"] = worker

            # Убираем пароль из session_state
            st.session_state.pop(
                "login_password",
                None,
            )

            st.rerun()


        else:

            st.error(
                "Неверный пароль."
            )


    return None


def logout():

    st.session_state.pop(
        "worker",
        None,
    )

    st.session_state.pop(
        "login_password",
        None,
    )

    st.rerun()
