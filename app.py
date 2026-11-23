"""
Точка входа PeerCheck: настройка страницы, меню и кнопка выхода.
Каждый экран лежит в отдельном файле в папке screens/, у каждого файла свой ответственный.
Запуск: python -m streamlit run app.py
"""
import streamlit as st

from database import init_db

st.set_page_config(page_title="PeerCheck", page_icon="📝", layout="wide")
init_db()

# Кто вошёл, видно в боковом меню на всех страницах
if "pseudonym" in st.session_state:
    st.sidebar.write(f"Ты вошёл как **{st.session_state['pseudonym']}**")
    if st.sidebar.button("Выйти"):
        del st.session_state["pseudonym"]
        st.rerun()

page = st.navigation([
    st.Page("screens/home.py", title="Как это работает", default=True),
    st.Page("screens/login.py", title="Вход и регистрация"),
    st.Page("screens/submit.py", title="Сдать лабораторную"),
    st.Page("screens/review.py", title="Проверить чужую работу"),
    st.Page("screens/my_reviews.py", title="Мои отзывы"),
])
page.run()
