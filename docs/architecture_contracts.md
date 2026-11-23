# Контракты модулей и схема данных

Здесь записано, **какие таблицы есть в базе** и **какие функции есть в каждом модуле**: как они называются, что принимают и что возвращают.

Зачем это нужно: интерфейс в `app.py` вызывает функции из `database.py` и `roulette.py`. Чтобы всё склеилось без переделок, имена и аргументы функций должны **совпадать с этим документом буква в букву**.

> Хочешь добавить или переименовать функцию? Сначала пиши наставнику, обновим этот файл, потом код.

У каждой функции указан статус:

| Статус | Что значит |
| :--- | :--- |
| **[есть]** | Функция уже в `main` и работает как описано |
| **[есть, исправить]** | Функция в `main`, но поведение пока расходится с описанием, ниже написано чем |
| **[задача #N]** | Функцию пишут в задаче #N |
| **[запланировано]** | Функции ещё нет ни в коде, ни в задачах. Не пиши её, пока она не появится в твоей задаче |

---

## 0. Учётная запись и анонимность

1. **Регистрация.** Студент регистрируется по своей почте и паролю. Пароль в открытом виде нигде не хранится: в базу пишется только его хеш (`hash_password`).
2. **Псевдоним.** При регистрации система сама выдаёт студенту случайный псевдоним (`generate_pseudonym()`, например `Скрытный Енот #427`) и проверяет по базе, что он не занят. Свой ник студент не придумывает: по знакомому нику однокурсники могли бы узнать автора.
3. **Вход.** Студент входит по почте и паролю, псевдоним помнить не нужно. После входа псевдоним лежит в `st.session_state["pseudonym"]`.
4. **Что видят другие.** Другим пользователям показывается **только псевдоним**. Почта и хеш пароля нужны только для входа и в интерфейсе не показываются.
5. **Псевдоним в базе и функциях.** Псевдоним постоянный и привязан к учётной записи. Именно он записывается в `student_token` и `reviewer_token` и передаётся как `current_user_token` во все функции ниже.

---

## 1. База данных SQLite (`peercheck.db`)

### Таблица `users`: учётные записи [задача #17]
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,             -- Почта для входа, в нижнем регистре. Другим не показывается
    password_hash TEXT NOT NULL,            -- Результат hash_password(), строка "соль$хеш"
    pseudonym TEXT NOT NULL UNIQUE,         -- Псевдоним из generate_pseudonym() ("Скрытный Енот #427")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `submissions`: сданные работы [есть]
```sql
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_number INTEGER NOT NULL,            -- Номер лабораторной (например, 1)
    file_path TEXT NOT NULL,                -- Путь к файлу на диске ("uploads/...")
    student_token TEXT,                     -- Псевдоним автора (users.pseudonym)
    is_reviewed INTEGER DEFAULT 0,          -- 0 — ждёт проверки, 1 — проверена
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время загрузки
);
```

### Таблица `reviews`: рецензии [задача #14]
```sql
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id INTEGER NOT NULL,                -- Ссылка на submissions(id)
    reviewer_token TEXT NOT NULL,           -- Псевдоним рецензента (users.pseudonym)
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

### Критерии оценки
Порядок оценок везде одинаковый: `ratings[0]` пишется в `c1_score`, `ratings[4]` в `c5_score`.

1. Полнота выполнения задания (код решает задачу).
2. Читаемость и структура кода (понятные имена, отступы).
3. Наличие скриншотов работы программы и тестов.
4. Качество оформления отчёта (цель, ход работы).
5. Наличие и осмысленность выводов.

---

## 2. `database.py`

```python
import sqlite3

DB_NAME = "peercheck.db"


def init_db() -> None:
    """
    Создаёт файл peercheck.db и таблицы, если их ещё нет. [есть]
    Сейчас создаёт submissions. Таблица reviews добавляется в задаче #14,
    таблица users — в задаче #17.
    """


def add_submission(student_token: str, lab_number: int, file_path: str) -> int:
    """Добавляет запись о сданной работе в submissions. Возвращает id новой записи. [есть]"""


def get_unreviewed_submissions() -> list[dict]:
    """
    Возвращает непроверенные работы (is_reviewed = 0) списком словарей
    в формате, который ждёт select_lab_for_review:
    [{"id": 1, "student_token": "Скрытный Енот #427", "lab_number": 1,
      "file_path": "uploads/..."}, ...]
    Если работ нет, возвращает [].

    [есть, исправить] Сейчас возвращает объекты sqlite3.Row, у них нет .get(),
    и select_lab_for_review на них падает. Исправление — шаг 1 задачи #14:
    return [dict(row) for row in rows]
    """


def add_review(lab_id: int, reviewer_token: str, ratings: list[int], comment: str) -> int:
    """
    Сохраняет рецензию: ratings[0..4] раскладывает по c1_score..c5_score,
    у работы lab_id ставит is_reviewed = 1. Возвращает id рецензии. [задача #14]
    """


def get_reviews_for_student(student_token: str) -> list[dict]:
    """
    Все рецензии на работы автора student_token (JOIN reviews и submissions по lab_id).
    Каждый словарь: id, lab_id, lab_number, reviewer_token, c1_score..c5_score,
    comment, created_at. Если рецензий нет, возвращает []. [задача #14]
    """


def get_student_counts(student_token: str) -> tuple[int, int]:
    """
    Возвращает (сколько работ сдал студент, сколько чужих работ он проверил).
    Нужно для can_view_own_reviews. [задача #14]
    """


def add_user(email: str, password_hash: str, pseudonym: str) -> int:
    """
    Добавляет учётную запись в users и возвращает её id. [задача #17]
    Почту перед записью приводит к виду email.strip().lower().
    Перед вызовом проверь, что get_user_by_email(email) вернул None:
    вторая запись с той же почтой не создастся (поле UNIQUE).
    """


def get_user_by_email(email: str) -> dict | None:
    """
    Ищет учётную запись по почте (тоже через email.strip().lower()). [задача #17]
    Возвращает {"id": 1, "email": "...", "password_hash": "...", "pseudonym": "..."}
    или None, если такой почты нет. Нужна только для входа и регистрации.
    """


def pseudonym_exists(pseudonym: str) -> bool:
    """Занят ли псевдоним кем-то из пользователей. [задача #17]"""
```

---

## 3. `roulette.py`

Сигнатуры `select_lab_for_review`, `validate_review`, `generate_pseudonym` и `calculate_final_score` проверяет `test_roulette.py`, менять их нельзя.

```python
import hashlib
import hmac
import os
import random
import uuid


def select_lab_for_review(current_user_token: str, available_labs: list[dict]) -> dict | None:
    """
    Выбирает случайную чужую работу для проверки. [есть]
    1. Исключить работы самого студента (student_token == current_user_token).
    2. Если подходящих работ нет, вернуть None.
    3. Иначе вернуть одну случайную через random.choice(...).
    """


def validate_review(ratings: list[int], comment: str) -> tuple[bool, str]:
    """
    Проверяет форму рецензии. [есть]
    1. В ratings ровно 5 оценок, каждая от 1 до 5.
    2. len(comment.strip()) >= 50.
    3. Текст не состоит из одного повторяющегося символа.
    Возвращает (True, "OK") или (False, "Текст ошибки").
    """


def generate_pseudonym() -> str:
    """
    Возвращает случайный псевдоним вида "Прилагательное Животное #число",
    число от 100 до 999. Пример: "Скрытный Енот #427". [есть]
    Занят ли псевдоним, функция не знает, это проверяет pseudonym_exists.
    """


def calculate_final_score(ratings: list[int]) -> float:
    """
    Средний балл по оценкам, округлённый до 1 знака: [5, 4, 5, 3, 4] -> 4.2.
    Для пустого списка возвращает 0.0. [есть]
    """


def can_view_own_reviews(submitted_count: int, reviewed_count: int) -> bool:
    """
    Можно ли студенту смотреть отзывы на свои работы. [есть]
    Правило баланса: сдана хотя бы одна работа (submitted_count > 0)
    и проверено чужих не меньше, чем сдано своих (reviewed_count >= submitted_count).
    Счётчики берутся из get_student_counts.
    """


def save_uploaded_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Сохраняет PDF в папку uploads/ (создаёт её при необходимости)
    и возвращает путь для add_submission. [есть, исправить]
    Имя файла на диске должна придумывать сама функция, например
    uuid.uuid4().hex + ".pdf". Исходное имя filename не используется:
    в нём бывает фамилия автора, а одинаковые имена затирают друг друга.
    Сейчас файл сохраняется под исходным именем, исправление в задаче #18.
    """


def validate_registration(email: str, password: str) -> tuple[bool, str]:
    """
    Проверяет форму регистрации. [задача #18]
    1. В почте есть "@" и точка после него.
    2. Пароль не короче 8 символов.
    Возвращает (True, "OK") или (False, "Текст ошибки").
    """


def hash_password(password: str) -> str:
    """
    Возвращает хеш пароля для записи в users.password_hash. [задача #18]
    Соль: os.urandom(16). Хеш: hashlib.pbkdf2_hmac("sha256", password.encode(), соль, 100_000).
    Результат — строка salt.hex() + "$" + хеш.hex(). Одинаковые пароли дают разные строки.
    """


def check_password(password: str, password_hash: str) -> bool:
    """
    Совпадает ли введённый пароль с сохранённым хешем. [задача #18]
    Разделить password_hash по "$", посчитать pbkdf2_hmac с той же солью
    и сравнить через hmac.compare_digest(...).
    """
```

---

## 4. `app.py` и экраны `screens/`

Каждый экран лежит в своём файле, у каждого файла свой ответственный, поэтому два человека не правят один файл.

| Файл | Что делает | Ответственный | Статус |
| :--- | :--- | :--- | :--- |
| `app.py` | `st.set_page_config(page_title="PeerCheck", page_icon="📝", layout="wide")`, `init_db()`, меню `st.navigation`, псевдоним и кнопка «Выйти» в боковом меню | наставник | **[есть]** |
| `screens/home.py` | «Как это работает» | Виталина | **[задача #22]**, сейчас заглушка |
| `screens/login.py` | «Вход и регистрация» | Егор | **[задача #24]**, сейчас временный вход по любому псевдониму |
| `screens/submit.py` | «Сдать лабораторную» | Виталина | **[задача #19]**, сейчас заглушка |
| `screens/review.py` | «Проверить чужую работу» | Егор | **[задача #21]**, сейчас заглушка |
| `screens/my_reviews.py` | «Мои отзывы» | Кирилл | **[задача #20]**, сейчас заглушка |

**Общее для экранов.** Все экраны, кроме «Как это работает» и «Вход и регистрация», начинаются с проверки входа:
```python
if "pseudonym" not in st.session_state:
    st.info("Сначала войди на странице «Вход и регистрация».")
    st.stop()
pseudonym = st.session_state["pseudonym"]
```
Дальше во все функции передаётся `pseudonym`.

**Что на каждом экране:**

* **«Как это работает»:** описание сервиса, четыре шага (регистрация, сдача, проверка чужой, отзывы), критерии оценки из раздела 1, пояснение, что почту другие не видят.
* **«Вход и регистрация»:** две вкладки `st.tabs`.
  * Регистрация: почта, пароль, повтор пароля, `validate_registration`. Если `get_user_by_email` вернул `None`, система генерирует псевдоним (повторяет `generate_pseudonym()`, пока `pseudonym_exists` возвращает `True`), затем `hash_password` и `add_user`. Студенту показывается его псевдоним с пояснением: другие видят только его.
  * Вход: почта и пароль, `get_user_by_email` и `check_password`. При успехе псевдоним записывается в `st.session_state["pseudonym"]`. На обе ошибки (нет такой почты, неверный пароль) одно сообщение «Неверная почта или пароль».
  * Почта и пароль нигде на экране не выводятся, кроме полей ввода (для пароля `type="password"`).
* **«Сдать лабораторную»:** номер работы (1–5, в коде числом через `format_func`), чекбокс «в файле нет титульного листа и ФИО», загрузка PDF до 15 МБ, отдельное предупреждение на каждую ошибку. При успехе `save_uploaded_pdf` и `add_submission`. **Поля никнейма нет.**
* **«Проверить чужую работу»:** `select_lab_for_review(pseudonym, get_unreviewed_submissions())`. Выданную работу нужно хранить в `st.session_state`, иначе при каждом движении ползунка Streamlit перезапускает страницу и рулетка выдаёт новую. Сплит-экран `st.columns([3, 2])`: слева `st.pdf(путь)`, справа 5 ползунков по критериям из раздела 1 и комментарий, затем `validate_review` и `add_review`.
* **«Мои отзывы»:** `get_student_counts` и `can_view_own_reviews`. Если доступа нет, показать, сколько работ ещё нужно проверить. Если есть, показать отзывы из `get_reviews_for_student` со средним баллом `calculate_final_score`.
