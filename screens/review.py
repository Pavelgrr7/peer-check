import streamlit as st
from database import add_review, get_unreviewed_submissions
from roulette import select_lab_for_review, validate_review

CRITERIA = [
    "1. Полнота выполнения задания (код решает задачу)",
    "2. Читаемость и структура кода (понятные имена, отступы)",
    "3. Наличие скриншотов работы программы и тестов",
    "4. Качество оформления отчёта (цель, ход работы)",
    "5. Наличие и осмысленность выводов",
]

st.title("Проверить чужую работу")

# Экран работает только после входа: псевдоним нужен, чтобы не выдать студенту его же работу
if "pseudonym" not in st.session_state:
    st.info("Сначала войди на странице «Вход и регистрация».")
    st.stop()
pseudonym = st.session_state["pseudonym"]

# Рулетку крутим один раз и запоминаем, кому выдали работу
if st.session_state.get("lab_owner") != pseudonym:
    st.session_state["lab_for_review"] = select_lab_for_review(pseudonym, get_unreviewed_submissions())
    st.session_state["lab_owner"] = pseudonym
lab = st.session_state["lab_for_review"]

# Пустая очередь
if lab is None:
    st.info("Чужих работ на проверку пока нет, загляни позже")

    if st.button("Проверить ещё раз"):
        del st.session_state["lab_owner"]
        st.rerun()

    st.stop()

# Сплит-экран
st.subheader(f"Лабораторная №{lab['lab_number']}")
left, right = st.columns([3, 2])  # слева 60% ширины, справа 40%

with left:
    st.pdf(lab["file_path"], height=700)

with right:
    ratings = []
    for criterion in CRITERIA:
        ratings.append(st.slider(criterion, 1, 5, 5))
    comment = st.text_area("Комментарий для автора (от 50 символов):")

    if st.button("Отправить рецензию"):
        ok, message = validate_review(ratings, comment)

        if not ok:
            st.warning(message)

        else:
            add_review(lab["id"], pseudonym, ratings, comment)
            del st.session_state["lab_owner"] #при следующем заходе рулетка выдаст новую работу
            st.success("Рецензия сохранена, спасибо! Обнови страницу, чтобы взять следующую работу.")