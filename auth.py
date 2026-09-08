import streamlit as st

# =========================================================

# ПОИСК ПОЛЬЗОВАТЕЛЯ ПО ПАРОЛЮ

# =========================================================

def get_user_by_password(
password,
):

```
# -----------------------------------------------------
# МЕРЧЕНДАЙЗЕРЫ
# -----------------------------------------------------

workers = st.secrets.get(
    "workers",
    {},
)

for worker, worker_password in workers.items():

    if password == worker_password:

        return (
            worker,
            "worker",
        )


# -----------------------------------------------------
# СУПЕРВАЙЗЕРЫ
# -----------------------------------------------------

supervisors = st.secrets.get(
    "supervisors",
    {},
)

for supervisor, supervisor_password in supervisors.items():

    if password == supervisor_password:

        return (
            supervisor,
            "supervisor",
        )


return (
    None,
    None,
)
```

# =========================================================

# ВХОД

# =========================================================

def login():

```
# -----------------------------------------------------
# ПРОВЕРЯЕМ, АВТОРИЗОВАН ЛИ ПОЛЬЗОВАТЕЛЬ
# -----------------------------------------------------

if (
    "user_name" in st.session_state
    and "user_role" in st.session_state
):

    return (
        st.session_state[
            "user_name"
        ],
        st.session_state[
            "user_role"
        ],
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

    key="login_password",
)


if st.button(

    "Войти",

    type="primary",

    use_container_width=True,
):


    # -------------------------------------------------
    # ПУСТОЙ ПАРОЛЬ
    # -------------------------------------------------

    if not password:

        st.warning(
            "Введите пароль."
        )

        return (
            None,
            None,
        )


    # -------------------------------------------------
    # ИЩЕМ ПОЛЬЗОВАТЕЛЯ
    # -------------------------------------------------

    user_name, user_role = (
        get_user_by_password(
            password
        )
    )


    # -------------------------------------------------
    # УСПЕШНЫЙ ВХОД
    # -------------------------------------------------

    if user_name:

        st.session_state[
            "user_name"
        ] = user_name

        st.session_state[
            "user_role"
        ] = user_role

        st.rerun()


    # -------------------------------------------------
    # НЕВЕРНЫЙ ПАРОЛЬ
    # -------------------------------------------------

    else:

        st.error(
            "Неверный пароль."
        )


return (
    None,
    None,
)
```

# =========================================================

# ВЫХОД

# =========================================================

def logout():

```
st.session_state.pop(

    "user_name",

    None,
)


st.session_state.pop(

    "user_role",

    None,
)


# На случай, если остался от старой версии

st.session_state.pop(

    "worker",

    None,
)


st.rerun()
```
