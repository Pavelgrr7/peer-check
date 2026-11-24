"""
Модуль работы с базой данных SQLite.
Отвечает за хранение сданных работ и рецензий.
"""
import sqlite3

from streamlit import cursor

DB_NAME = "peercheck.db"

# 1. Сущность "Сданная лабораторная работа" (Submission)
# - id: уникальный номер работы (int)
# - student_token: анонимный хэш/ID автора (str)
# - lab_number: номер лабораторной (int)
# - file_path: путь к сохраненному PDF-файлу на диске (str)
# - upload_date: дата и время загрузки (str/datetime)
# - is_reviewed: проверена ли работа (bool, по умолчанию False)

# 2. Сущность "Рецензия" (Review)
# - id: уникальный номер отзыва (int)
# - lab_id: ссылка на проверенную работу (int)
# - reviewer_token: анонимный ID проверяющего (str)
# - score_criteria: словарь или строка с оценками по 5 критериям (int/str)
# - comment: текстовый комментарий с замечаниями (str)
# - created_at: дата проверки (str/datetime)

def init_db():
    """Создаёт файл peercheck.db и таблицу submissions, если их ещё нет."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
    """CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_number INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    student_token TEXT,
    is_reviewed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute(
    '''CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id INTEGER NOT NULL,
    reviewer_token TEXT NOT NULL,
    c1_score INTEGER NOT NULL,
    c2_score INTEGER NOT NULL,
    c3_score INTEGER NOT NULL,
    c4_score INTEGER NOT NULL,
    c5_score INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lab_id) REFERENCES submissions(id))''')

    conn.commit()
    conn.close()
    print("База данных и таблица submissions успешно созданы!")

def add_submission(student_token: str, lab_number: int, file_path: str) -> int:
    """
    Добавляет запись о сданной работе в таблицу submissions.
    Возвращает id новой записи.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO submissions (student_token, lab_number, file_path) VALUES (?, ?, ?)",
    (student_token, lab_number, file_path))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id
    pass

def get_unreviewed_submissions() -> list[dict]:
    """
    Возвращает список всех непроверенных работ (где is_reviewed = 0)
    в виде списка словарей для алгоритма рулетки.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id, student_token, lab_number, file_path FROM submissions WHERE is_reviewed = 0")

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
    pass

def add_review(lab_id: int, reviewer_token: str, ratings: list[int], comment: str) -> int:
    """
    Сохраняет рецензию с 5 оценками в reviews и ставит is_reviewed = 1 у работы в submissions.
    Возвращает id созданной рецензии.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO reviews (lab_id, reviewer_token, c1_score, c2_score, c3_score, c4_score, c5_score, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    (lab_id, reviewer_token, ratings[0], ratings[1], ratings[2], ratings[3], ratings[4], comment))
    review_id = cursor.lastrowid

    cursor.execute(
    "UPDATE submissions SET is_reviewed = 1 WHERE id = ?",
    (lab_id,))

    conn.commit()
    conn.close()
    return review_id

def get_reviews_for_student(student_token: str) -> list[dict]:
    """
    Возвращает все рецензии, оставленные на работы автора student_token.
    Соединяет таблицы reviews и submissions по lab_id.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
    """SELECT r.id, r.lab_id, s.lab_number, r.reviewer_token,
                r.c1_score, r.c2_score, r.c3_score, r.c4_score, r.c5_score,
                r.comment, r.created_at
    FROM reviews r
    JOIN submissions s ON r.lab_id = s.id
    WHERE s.student_token = ?""",
    (student_token,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_student_counts(student_token: str) -> tuple[int, int]:
    """
    Возвращает кортеж (сколько лаб сдал студент, сколько чужих лаб он проверил).
    Нужно для проверки доступа can_view_own_reviews.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM submissions WHERE student_token = ?",
        (student_token,))
    submitted_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM reviews WHERE reviewer_token = ?",
        (student_token,))
    reviewed_count = cursor.fetchone()[0]

    conn.close()
    return (submitted_count, reviewed_count)

if __name__ == "__main__":
    init_db()
    sub_id = add_submission("Енот #100", 1, "uploads/test.pdf")
    print("Непроверенные до ревью:", get_unreviewed_submissions())

    rev_id = add_review(sub_id, "Лис #200", [5, 4, 5, 3, 4], "Отличная работа, все требования выполнены!")
    print("Добавлен отзыв ID:", rev_id)

    print("Статистика Енота (сдал, проверил):", get_student_counts("Енот #100"))
    print("Статистика Лиса (сдал, проверил):", get_student_counts("Лис #200"))
    print("Отзывы на работы Енота:", get_reviews_for_student("Енот #100"))