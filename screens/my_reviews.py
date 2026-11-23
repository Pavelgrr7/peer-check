import streamlit as st

st.title("Мои отзывы")

# Экран работает только после входа: по псевдониму ищем отзывы на работы студента
if "pseudonym" not in st.session_state:
    st.info("Сначала войди на странице «Вход и регистрация».")
    st.stop()
pseudonym = st.session_state["pseudonym"]

st.info("Экран в работе: задача «Экран „Мои отзывы“».")
