"""
Тестовый сценарий для проверки модуля roulette.py
Запуск: python test_roulette.py
"""
import sys

try:
    from roulette import select_lab_for_review, validate_review
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что функции select_lab_for_review и validate_review объявлены в roulette.py")
    sys.exit(1)


def run_tests():
    total_tests = 5
    passed = 0

    print("Запуск проверки бизнес-логики (roulette.py)...")

    # Тест 1: Исключение своей работы
    mock_labs = [
        {"id": 1, "student_token": "egor", "lab_number": 1},
        {"id": 2, "student_token": "kirill", "lab_number": 1},
    ]
    chosen = select_lab_for_review("egor", mock_labs)
    if chosen and chosen["student_token"] != "egor":
        print("[1/5] Алгоритм не выдает студенту его собственную работу")
        passed += 1
    else:
        print("[1/5] Ошибка: алгоритм вернул работу самого пользователя!")

    # Тест 2: Пустая очередь / нет чужих работ
    only_own_labs = [{"id": 1, "student_token": "egor", "lab_number": 1}]
    chosen_empty = select_lab_for_review("egor", only_own_labs)
    if chosen_empty is None:
        print("[2/5] Возврат None, если доступных чужих работ нет")
        passed += 1
    else:
        print("[2/5] Ошибка: если доступных работ нет, функция должна возвращать None")

    # Тест 3: Корректный отзыв проходит валидацию
    valid_ratings = [5, 4, 5, 4, 5]
    good_comment = "Код написан аккуратно, переменные названы понятно. Добавлены скриншоты тестов."
    is_ok, msg = validate_review(valid_ratings, good_comment)
    if is_ok is True:
        print("[3/5] Качественный отзыв успешно проходит валидацию")
        passed += 1
    else:
        print(f"[3/5] Ошибка: корректный отзыв был отклонен ({msg})")

    # Тест 4: Слишком короткий отзыв блокируется
    is_ok, msg = validate_review([5, 5, 5, 5, 5], "все ок норм")
    if is_ok is False:
        print("[4/5] Защита от коротких отписок (< 50 символов) работает")
        passed += 1
    else:
        print("[4/5] Ошибка: валидатор пропустил короткую отписку!")

    # Тест 5: Некорректные оценки
    is_ok_ratings, _ = validate_review([5, 4], good_comment) # мало оценок
    is_ok_range, _ = validate_review([6, 5, 4, 3, 2], good_comment) # оценка 6
    if is_ok_ratings is False and is_ok_range is False:
        print("[5/5] Проверка списка оценок (строго 5 чисел от 1 до 5) работает")
        passed += 1
    else:
        print("[5/5] Ошибка: валидатор пропустил неверное количество оценок или значения вне [1..5]")

    if passed == total_tests:
        print("Тесты успешно пройдены. Можно делать коммит и пуш в github")
    else:
        print(f"Пройдено тестов: {passed}/{total_tests}. Поправь код в roulette.py и запустите снова.")


if __name__ == "__main__":
    run_tests()