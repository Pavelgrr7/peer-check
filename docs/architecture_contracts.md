# Контракты модулей и схема данных

Здесь записано, **какие таблицы есть в базе** и **какие функции есть в каждом модуле**: как они называются, что принимают и что возвращают.

Зачем это нужно: Виталина в `app.py` будет вызывать функции Кирилла и Егора. Чтобы всё склеилось без переделок, имена и аргументы функций должны **совпадать с этим документом буква в букву**.

> Хочешь добавить или переименовать функцию? Сначала пиши наставнику, обновим этот файл, потом код.

---

## 1. База данных SQLite (`peercheck.db`)

### Таблица `submissions`: сданные работы (Спринт 2)
```sql
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_number INTEGER NOT NULL,            -- Номер лабораторной (например, 1)
    file_path TEXT NOT NULL,                -- Путь к файлу на диске ("uploads/...")
    student_token TEXT,                     -- Никнейм автора ("user_123")
    is_reviewed INTEGER DEFAULT 0,          -- 0 — ждёт проверки, 1 — проверена
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время загрузки
);
```

### Таблица `reviews`: рецензии (появится в следующих спринтах)
```sql
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id INTEGER NOT NULL,                -- Ссылка на submissions(id)
    reviewer_token TEXT NOT NULL,           -- Никнейм рецензента
    c1_score INTEGER NOT NULL,              -- Оценка по критерию 1 (1–5)
    c2_score INTEGER NOT NULL,              -- Оценка по критерию 2 (1–5)
    c3_score INTEGER NOT NULL,              -- Оценка по критерию 3 (1–5)
    c4_score INTEGER NOT NULL,              -- Оценка по критерию 4 (1–5)
    c5_score INTEGER NOT NULL,              -- Оценка по критерию 5 (1–5)
    comment TEXT NOT NULL,                  -- Текст отзыва (от 50 символов)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lab_id) REFERENCES submissions(id)
);
```

---

## 2. `database.py`

```python
import sqlite3

DB_NAME = "peercheck.db"


def init_db() -> None:
    """Создаёт файл peercheck.db и таблицу submissions, если их ещё нет."""


def add_submission(student_token: str, lab_number: int, file_path: str) -> int:
    """Добавляет запись о сданной работе в submissions. Возвращает id новой записи."""


def get_all_submissions() -> list[dict]:
    """
    Возвращает все сданные работы списком словарей:
    [{"id": 1, "student_token": "user_123", "lab_number": 1,
      "file_path": "uploads/...", "is_reviewed": 0}, ...]
    Если работ нет, возвращает [].
    """
```

---

## 3. `roulette.py`

Сигнатуры `select_lab_for_review` и `validate_review` проверяет `test_roulette.py`, менять их нельзя.

```python
import random


def select_lab_for_review(current_user_token: str, available_labs: list[dict]) -> dict | None:
    """
    Выбирает случайную чужую работу для проверки.
    1. Исключить работы самого студента (student_token == current_user_token).
    2. Если подходящих работ нет, вернуть None.
    3. Иначе вернуть одну случайную через random.choice(...).
    """


def validate_review(ratings: list[int], comment: str) -> tuple[bool, str]:
    """
    Проверяет форму рецензии.
    1. В ratings ровно 5 оценок, каждая от 1 до 5.
    2. len(comment.strip()) >= 50.
    3. Текст не состоит из одного повторяющегося символа.
    Возвращает (True, "OK") или (False, "Текст ошибки").
    """


def can_view_own_reviews(current_user_token: str) -> bool:
    """
    Проверил ли студент хотя бы одну чужую работу (тогда ему открываются отзывы на свою).
    Реализуем в следующих спринтах, сигнатура может уточниться.
    """
```

---

## 4. `app.py`

1. **Настройка страницы:** `st.set_page_config(page_title="PeerCheck", page_icon="📝", layout="wide")`.
2. **Разделы в боковом меню** (`st.sidebar.radio`):
   * «Сдать лабораторную»: поле никнейма, номер работы, чекбокс анонимности, загрузка PDF (до 15 МБ).
   * «Проверить чужую работу»: вызов `select_lab_for_review`, сплит-экран (PDF слева, 5 оценок и комментарий справа).
   * «Мои отзывы»: оценки на свою работу после выполнения своей проверки.
