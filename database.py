"""
Модуль работы с базой данных SQLite.
Отвечает за хранение сданных работ и рецензий.
"""
import sqlite3

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
    # Эта настройка позволяет обращаться к колонкам по именам, как к словарю:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id, student_token, lab_number, file_path FROM submissions WHERE is_reviewed = 0")

    rows = cursor.fetchall()
    conn.close()
    return rows
    pass

if __name__ == "__main__":
    init_db()
    new_id = add_submission("test_user", 1, "uploads/test.pdf")
    print(f"Добавлена тестовая запись с id = {new_id}")

    all_labs = get_unreviewed_submissions()
    print("Список работ в базе:", all_labs)