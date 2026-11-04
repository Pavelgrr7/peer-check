"""
Модуль бизнес-логики сервиса PeerCheck.
Отвечает за правила назначения работ и проверки доступа.
"""

import random


def select_lab_for_review(current_user_token: str, available_labs: list[dict]) -> dict | None:
    """
    Выбирает случайную работу для проверки.

    available_labs - это список словарей вида:
    [
        {"id": 1, "student_token": "user_123", "lab_number": 1},
        {"id": 2, "student_token": "user_456", "lab_number": 1},
    ]

    Алгоритм:
    1. Отфильтровать список: оставить только те работы, где student_token НЕ равен current_user_token (нельзя проверять свою же работу).
    2. Если подходящих работ нет - вернуть None.
    3. Если работы есть - выбрать одну случайную через random.choice(...) и вернуть её.
    """

    candidates = [lab for lab in available_labs if lab.get("student_token") != current_user_token] #Фильтруем работы, исключая собственные

    if not candidates:
        return None #Если подходящих работ нет — возвращаем None

    return random.choice(candidates) #Выбираем случайную работу


def can_view_own_reviews(current_user_token: str) -> bool:
    """
    Проверяет, имеет ли право студент смотреть отзывы на свою работу.

    Правило:
    Доступ разрешен ТОЛЬКО если студент уже отправил хотя бы 1 качественную
    рецензию на чужую работу.

    current_user_token: Анонимный идентификатор студента.
    True, если доступ открыт, иначе False.
    """
    # Заглушка: пока доступ закрыт
    return False


def validate_review(ratings: list[int], comment: str) -> tuple[bool, str]:
    """
    Проверяет корректность заполнения формы рецензии.

    Правила:
    1. Список ratings должен содержать ровно 5 оценок, и каждая оценка должна быть от 1 до 5.
    2. Длина текста comment (без учета лишних пробелов по краям) должна быть не менее 50 символов.
    3. Текст не должен состоять из одного повторяющегося символа (например, "ааааааа...").
    Проверить это всё можно через if/else.

    Возвращает:
    - (True, "OK") - если всё заполнено честно.
    - (False, "Текст ошибки") - если есть нарушение (например: "Отзыв слишком короткий").
    """
    #В форме должно быть ровно 5 оценок.
    if len(ratings) != 5:
        return (False, "Должно быть ровно 5 оценок")

    #Каждая оценка должна укладываться в шкалу от 1 до 5.
    for rating in ratings:
        if not (1 <= rating <= 5):
            return (False, "Каждая оценка должна быть от 1 до 5")

    #Убираем пробелы по краям
    text = comment.strip()

    #Длина текста отзыва должна быть не менее 50 символов
    if len(text) < 50:
        return (False, "Отзыв слишком короткий")

    #Текст отзыва не должен состоять из одного повторяющегося символа
    if len(set(text)) == 1:
        return (False, "Текст не должен состоять из одного повторяющегося символа")

    return (True, "OK") #Всё заполнено честно


if __name__ == "__main__":
    labs = [
        {"id": 1, "student_token": "egor", "lab_number": 1},
        {"id": 2, "student_token": "kirill", "lab_number": 1},
    ]
    print("Работа для egor:", select_lab_for_review("egor", labs))
    print("Отписка:", validate_review([5, 5, 5, 5, 5], "норм"))