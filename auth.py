import streamlit as st

# =========================================================

# ПОИСК МЕРЧЕНДАЙЗЕРА ПО ПАРОЛЮ

# =========================================================

def get_worker_by_password(
password,
):

```
workers = st.secrets.get(
    "workers",
    {},
)

for worker, worker_password in workers.items():

    if password == worker_password:

        return worker

return None
```

# =========================================================

# ПРОВЕРКА СУПЕРВАЙЗЕРА

# =========================================================

def is_supervisor_password(
password,
):

```
supervisor_password = (
    st.secrets.get(
        "supervisor_password",
        "",
    )
)

return (
    password
    == supervisor_password
)
```

# =========================================================

# ВХОД

# =========================================================

def login():

```
# -----------------------------------------------------
# ЕСЛИ ПОЛЬЗОВАТЕЛЬ УЖЕ ВОШЁЛ
# -----------------------------------------------------

if "user_type" in st.session_state:

    return (
        st.session_state["user_type"],
        st.session_state["user_name"],
    )


# -----------------------------------------------------
# ЭКРАН ВХОДА
# -----------------------------------------------------

st.title(
    "📍 Маршруты мерчендайзеров"
)

st.caption(
    "Введите пароль"
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
    # СУПЕРВАЙЗЕР
    # -------------------------------------------------

    if is_supervisor_password(
        password
    ):

        st.session_state[
            "user_type"
        ] = "supervisor"

        st.session_state[
            "user_name"
        ] = "Супервайзер"

        st.rerun()


    # -------------------------------------------------
    # МЕРЧЕНДАЙЗЕР
    # -------------------------------------------------

    worker = (
        get_worker_by_password(
            password
        )
    )


    if worker:

        st.session_state[
            "user_type"
        ] = "worker"

        st.session_state[
            "user_name"
        ] = worker

        st.rerun()


    else:

        st.error(
            "Неверный пароль."
        )


return None, None
```

# =========================================================

# ВЫХОД

# =========================================================

def logout():

```
st.session_state.pop(
    "user_type",
    None,
)

st.session_state.pop(
    "user_name",
    None,
)

st.rerun()
```
