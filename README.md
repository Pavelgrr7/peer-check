# PeerCheck

Веб-сервис анонимного взаимного рецензирования лабораторных работ: студент загружает свою работу в PDF, проверяет чужую по чек-листу и после этого получает отзывы на свою.

**Стек:** Python, Streamlit (интерфейс), SQLite (база данных).

## Кто за что отвечает

| Файл | Что в нём | Ответственный |
| :--- | :--- |:--------------|
| `app.py` | Интерфейс сайта (Streamlit) | Виталина      |
| `database.py` | Работа с базой данных SQLite | Кирилл        |
| `roulette.py` | Логика: выдача работ на проверку, проверка отзывов | Егор          |
| `test_roulette.py` | Автотесты для `roulette.py` (запуск: `python test_roulette.py`) | Паша          |
| `seed_demo_data.py` | Наполняет базу тестовыми работами (запуск: `python seed_demo_data.py`) | Паша          |

## Как запустить проект локально

1. Склонировать репозиторий и создать виртуальное окружение (подробно в [git_guide.md](docs/git_guide.md)).
2. Установить зависимости: `pip install -r requirements.txt`
3. Запустить приложение: `streamlit run app.py`

Для Виталины: в браузере через [GitHub Codespaces](docs/codespaces_guide.md).

## Доска с задачами

[Открыть Kanban-доску в GitHub Projects](https://github.com/users/Pavelgrr7/projects/2). Задачи сгруппированы по спринтам через [Milestones](https://github.com/Pavelgrr7/peer-check/milestones).

## Документация: читать в этом порядке

1. [Настройка PyCharm и основы Git](docs/git_guide.md): один раз в начале.
2. [Работа в Codespaces](docs/codespaces_guide.md): если работаешь в браузере, а не в PyCharm.
3. [Ежедневная работа с ветками и Pull Request](docs/daily_workflow_guide.md): понадобится, когда начнём работать через ветки (об этом предупрежу отдельно).
4. [Контракты модулей](docs/architecture_contracts.md): какие функции есть в `database.py` и `roulette.py` и что они принимают и возвращают.
5. Руководства к задачам Спринта 1: [UI](docs/ui_guide_s1.md), [База данных](docs/db_guide_s1.md), [Логика](docs/logic_guide_s1.md).
6. [Зачем нужна база данных и как работает SQLite](docs/tasks/sqlite_intro.md).

Если что-то не получается, пиши в чат в Telegram, разберёмся вместе
