"""
Наполняет базу тестовыми работами, чтобы было что проверять с первого запуска.
Создаёт peercheck.db, таблицу submissions и каталог uploads/ с 3 демо-PDF.
Запуск: python seed_demo_data.py
"""

import sqlite3
from pathlib import Path

DB_NAME = "peercheck.db"
UPLOADS_DIR = Path("uploads")


def create_minimal_pdf(file_path: Path, title: str, text: str) -> None:
    """Создаёт простой одностраничный PDF без сторонних библиотек (только латиница)."""
    content = f"BT /F1 16 Tf 50 720 Td ({title}) Tj 0 -30 Td /F1 11 Tf ({text}) Tj ET"
    objects = [
        "<</Type /Catalog /Pages 2 0 R>>",
        "<</Type /Pages /Kids [3 0 R] /Count 1>>",
        "<</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> "
        "/MediaBox [0 0 595 842] /Contents 5 0 R>>",
        "<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>",
        f"<</Length {len(content)}>>\nstream\n{content}\nendstream",
    ]

    # В PDF в конце файла хранится таблица (xref) с позицией каждого объекта в байтах
    pdf = "%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{number} 0 obj\n{body}\nendobj\n"

    xref_start = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += f"trailer <</Size {len(objects) + 1} /Root 1 0 R>>\nstartxref\n{xref_start}\n%%EOF\n"

    file_path.write_bytes(pdf.encode("ascii"))


def seed() -> None:
    UPLOADS_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Та же схема, что в docs/architecture_contracts.md
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lab_number INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            student_token TEXT,
            is_reviewed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM submissions")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"В {DB_NAME} уже есть {count} записей, демо-данные не добавляются.")
        conn.close()
        return

    demo_labs = [
        ("demo_ivan", 1, "demo_lab1_ivan.pdf", "Lab 1 (Variant 4)", "Linear List Implementation in Python"),
        ("demo_anna", 1, "demo_lab1_anna.pdf", "Lab 1 (Variant 7)", "Sorting Algorithms and Complexity"),
        ("demo_maxim", 1, "demo_lab1_maxim.pdf", "Lab 1 (Variant 12)", "Parsing and SQLite Storage"),
    ]

    for token, lab_number, filename, title, text in demo_labs:
        target_file = UPLOADS_DIR / filename
        create_minimal_pdf(target_file, title, text)

        # as_posix() даёт путь со слешем "/" и на Windows, и на Linux
        cursor.execute(
            "INSERT INTO submissions (student_token, lab_number, file_path) VALUES (?, ?, ?)",
            (token, lab_number, target_file.as_posix()),
        )
        print(f"[OK] Добавлена работа {filename} от {token}")

    conn.commit()
    conn.close()
    print(f"Готово: в {DB_NAME} 3 демо-работы, файлы лежат в {UPLOADS_DIR}/")


if __name__ == "__main__":
    seed()
