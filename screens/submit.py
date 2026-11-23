import streamlit as st

st.title("Сдать лабораторную")

# Экран работает только после входа: псевдоним нужен, чтобы записать работу на автора
if "pseudonym" not in st.session_state:
    st.info("Сначала войди на странице «Вход и регистрация».")
    st.stop()
pseudonym = st.session_state["pseudonym"]

st.info("Экран в работе: задача «Экран „Сдать лабораторную“».")
