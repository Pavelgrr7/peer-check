"""
Модуль бизнес-логики сервиса PeerCheck.
Отвечает за правила назначения работ и проверки доступа.
"""
import os
import random
import hashlib
import hmac
import uuid


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


def can_view_own_reviews(submitted_count: int, reviewed_count: int) -> bool:
    """
    Проверяет, имеет ли право студент смотреть отзывы на свои работы.

    Правило:
    1. Студент должен сдать хотя бы одну работу (submitted_count > 0).
    2. Количество проверенных им чужих работ должно быть >= количеству его сданных работ
       (reviewed_count >= submitted_count).
    """
    return submitted_count > 0 and reviewed_count >= submitted_count


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

def generate_pseudonym() -> str:
    """
    Генерирует случайный анонимный псевдоним вида: 'Прилагательное Животное #Число'.
    Пример: 'Скрытный Енот #427'
    """
    adjectives = [
        'Быстрый', 'Умный', 'Скрытный', 'Весёлый',
        'Логичный', 'Анонимный', 'Хитрый', 'Отважный',
    ]

    animals = [
        'Енот', 'Кот', 'Пингвин', 'Бобёр',
        'Хакер', 'Сова', 'Лис', 'Волк',
    ]

    adjective = random.choice(adjectives)
    animal = random.choice(animals)
    number = random.randint(100, 999)

    return f"{adjective} {animal} #{number}"

def calculate_final_score(ratings: list[int]) -> float:
    """
    Вычисляет средний балл по списку оценок и округляет его до 1 знака после запятой.

    :param ratings: Список оценок от рецензента, например: [5, 4, 5, 3, 4]
    :return: Среднее арифметическое (float), например: 4.2

    Важно: если список ratings пустой, функция должна возвращать 0.0,
    чтобы программа не упала с ошибкой деления на ноль (ZeroDivisionError).
    """
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings), 1)


def save_uploaded_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Сохраняет загруженный PDF-файл в папку 'uploads' и возвращает путь к нему.

    Исходное имя файла (filename) намеренно НЕ используется при сохранении
    на диске. Имя генерирует система, так как использование оригинального имени
    приводит к двум проблемам:
    1. Коллизии: файлы с одинаковыми именами (например, report.pdf) затирают
       друг друга, из-за чего в базе отображается чужая работа.
    2. Анонимность: имена вида Ivanov_lab1.pdf раскрывают личность студента,
       что недопустимо при анонимной проверке.

    :return: Путь к сохраненному файлу (например, 'uploads/a1b2c3d4....pdf').
    """
    upload_dir = "uploads"

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{uuid.uuid4().hex}.pdf")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path


def validate_registration(email: str, password: str) -> tuple[bool, str]:
    """
    Проверяет форму регистрации.

    Правила:
    1. В почте есть "@".
    2. После "@" есть точка (tpu.ru, mail.ru).
    3. Пароль не короче 8 символов.

    Возвращает (True, "OK") или (False, "Понятный текст ошибки").
    """
    if "@" not in email:
        return False, "В адресе электронной почты должен быть символ '@'"

    if "." not in email.split("@")[-1]:
        return False, "После символа '@' должен быть указан домен с точкой (например, tpu.ru)"

    if len(password) < 8:
        return False, "Пароль должен содержать не менее 8 символов"

    return True, "OK"


def hash_password(password: str) -> str:
    """
    Возвращает строку "соль$хеш" для записи в базу (users.password_hash).
    Одинаковые пароли дают разные строки, потому что соль каждый раз новая.
    """
    salt = os.urandom(16)  # 16 случайных байт
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)

    return f"{salt.hex()}${digest.hex()}"


def check_password(password: str, password_hash: str) -> bool:
    """
    Проверяет, совпадает ли введённый пароль с сохранённым хешем.
    """
    #Разделяем сохраненный хеш на соль и сам хеш
    salt_hex, digest_hex = password_hash.split("$")

    #Восстанавливаем соль из hex-строки в байты и считаем хеш для введенного пароля
    salt = bytes.fromhex(salt_hex)
    new_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)

    #Сравниваем результаты
    return hmac.compare_digest(new_digest.hex(), digest_hex)


if __name__ == "__main__":
    labs = [
        {"id": 1, "student_token": "egor", "lab_number": 1},
        {"id": 2, "student_token": "kirill", "lab_number": 1},
    ]
    print("Работа для egor:", select_lab_for_review("egor", labs))
    print("Отписка:", validate_review([5, 5, 5, 5, 5], "норм"))

    print("\nПроверка генерации псевдонимов и подсчёта средней оценки")
    print("Сгенерированный псевдоним 1:", generate_pseudonym())
    print("Сгенерированный псевдоним 2:", generate_pseudonym())

    sample_ratings = [5, 4, 5, 3, 4]
    print(f"Оценки: {sample_ratings} -> Средний балл:", calculate_final_score(sample_ratings))
    print("Пустой список -> Средний балл:", calculate_final_score([]))

    print("\nПроверка доступа к отзывам:")
    print("Сдал 1, проверил 0 -> Доступ:", can_view_own_reviews(1, 0))  # Ожидаем False
    print("Сдал 1, проверил 1 -> Доступ:", can_view_own_reviews(1, 1))  # Ожидаем True
    print("Сдал 2, проверил 1 -> Доступ:", can_view_own_reviews(2, 1))  # Ожидаем False (нужно проверить вторую!)

    print("\nПроверка сохранения файла:")
    saved_path = save_uploaded_pdf(b"%PDF-1.4 test bytes", "test_lab.pdf")
    print("Файл сохранен по пути:", saved_path)
    print("Файл реально существует на диске?", os.path.exists(saved_path))

    print("\nПроверка регистрации:")
    print(validate_registration("student@tpu.ru", "qwerty123"))  # (True, 'OK')
    print(validate_registration("student.tpu.ru", "qwerty123"))  # нет @
    print(validate_registration("student@tpu.ru", "123"))        # короткий пароль

    stored = hash_password("qwerty123")
    print("Хеш:", stored)
    print("Верный пароль:", check_password("qwerty123", stored))    # True
    print("Неверный пароль:", check_password("qwerty124", stored))  # False