import streamlit as st

st.title("Проверить чужую работу")

# Экран работает только после входа: псевдоним нужен, чтобы не выдать студенту его же работу
if "pseudonym" not in st.session_state:
    st.info("Сначала войди на странице «Вход и регистрация».")
    st.stop()
pseudonym = st.session_state["pseudonym"]

st.info("Экран в работе: задача «Экран „Проверить чужую работу“».")
