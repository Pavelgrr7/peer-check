"""
Модуль работы с базой данных SQLite.
Отвечает за хранение сданных работ и рецензий.
"""
import sqlite3

DB_NAME = "peercheck.db"

# В следующем спринте мы подключим библиотеку sqlite3 или peewee

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

if __name__ == "__main__":
    init_db()