import streamlit as st

from auth import (
login,
)

from routes import (
load_routes,
)

from pages.worker_dashboard import (
show_worker_dashboard,
)

from pages.supervisor_dashboard import (
show_supervisor_dashboard,
)

# =========================================================

# НАСТРОЙКИ

# =========================================================

st.set_page_config(
page_title="Маршруты мерчендайзеров",
page_icon="📍",
layout="wide",
)

# =========================================================

# АВТОРИЗАЦИЯ

# =========================================================

user_type, user_name = (
login()
)

if not user_type:

```
st.stop()
```

# =========================================================

# ЗАГРУЗКА МАРШРУТОВ

# =========================================================

try:

```
df = load_routes()
```

except Exception as error:

```
st.error(
    f"Ошибка загрузки маршрутов: "
    f"{error}"
)

st.stop()
```

# =========================================================

# СУПЕРВАЙЗЕР

# =========================================================

if user_type == "supervisor":

```
show_supervisor_dashboard(
    df
)
```

# =========================================================

# МЕРЧЕНДАЙЗЕР

# =========================================================

elif user_type == "worker":

```
show_worker_dashboard(
    df,
    user_name,
)
```
