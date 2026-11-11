"""
Тестовый сценарий для проверки модуля roulette.py
Запуск: python test_roulette.py
"""
import sys

try:
    import roulette
    from roulette import select_lab_for_review, validate_review
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедись, что функции select_lab_for_review и validate_review объявлены в roulette.py")
    sys.exit(1)


def run_tests():
    total_tests = 7
    passed = 0

    print("Запуск проверки бизнес-логики (roulette.py)...")

    # Тест 1: Исключение своей работы
    mock_labs = [
        {"id": 1, "student_token": "egor", "lab_number": 1},
        {"id": 2, "student_token": "kirill", "lab_number": 1},
    ]
    chosen = select_lab_for_review("egor", mock_labs)
    if chosen and chosen["student_token"] != "egor":
        print("[1/7] Алгоритм не выдает студенту его собственную работу")
        passed += 1
    else:
        print("[1/7] Ошибка: алгоритм вернул работу самого пользователя!")

    # Тест 2: Пустая очередь / нет чужих работ
    only_own_labs = [{"id": 1, "student_token": "egor", "lab_number": 1}]
    chosen_empty = select_lab_for_review("egor", only_own_labs)
    if chosen_empty is None:
        print("[2/7] Возврат None, если доступных чужих работ нет")
        passed += 1
    else:
        print("[2/7] Ошибка: если доступных работ нет, функция должна возвращать None")

    # Тест 3: Корректный отзыв проходит валидацию
    valid_ratings = [5, 4, 5, 4, 5]
    good_comment = "Код написан аккуратно, переменные названы понятно. Добавлены скриншоты тестов."
    is_ok, msg = validate_review(valid_ratings, good_comment)
    if is_ok is True:
        print("[3/7] Качественный отзыв успешно проходит валидацию")
        passed += 1
    else:
        print(f"[3/7] Ошибка: корректный отзыв был отклонен ({msg})")

    # Тест 4: Слишком короткий отзыв блокируется
    is_ok, msg = validate_review([5, 5, 5, 5, 5], "все ок норм")
    if is_ok is False:
        print("[4/7] Защита от коротких отписок (< 50 символов) работает")
        passed += 1
    else:
        print("[4/7] Ошибка: валидатор пропустил короткую отписку!")

    # Тест 5: Некорректные оценки
    is_ok_ratings, _ = validate_review([5, 4], good_comment) # мало оценок
    is_ok_range, _ = validate_review([6, 5, 4, 3, 2], good_comment) # оценка 6
    if is_ok_ratings is False and is_ok_range is False:
        print("[5/7] Проверка списка оценок (строго 5 чисел от 1 до 5) работает")
        passed += 1
    else:
        print("[5/7] Ошибка: валидатор пропустил неверное количество оценок или значения вне [1..5]")

    # Тест 6: Формат псевдонима "Слово Слово #123" (задача #13)
    generate_pseudonym = getattr(roulette, "generate_pseudonym", None)
    if generate_pseudonym is None:
        print("[6/7] Функция generate_pseudonym ещё не написана (задача #13)")
    else:
        pseudonym = generate_pseudonym()
        parts = pseudonym.split(" #") if isinstance(pseudonym, str) else []
        if (len(parts) == 2 and len(parts[0].split()) == 2
                and parts[1].isdigit() and 100 <= int(parts[1]) <= 999):
            print(f"[6/7] Псевдоним в нужном формате: {pseudonym}")
            passed += 1
        else:
            print(f"[6/7] Ошибка: псевдоним '{pseudonym}' не в формате 'Слово Слово #123' (число от 100 до 999)")

    # Тест 7: Средний балл и защита от пустого списка (задача #13)
    calculate_final_score = getattr(roulette, "calculate_final_score", None)
    if calculate_final_score is None:
        print("[7/7] Функция calculate_final_score ещё не написана (задача #13)")
    else:
        score = calculate_final_score([5, 4, 5, 3, 4])
        try:
            empty_score = calculate_final_score([])
        except ZeroDivisionError:
            empty_score = "ошибка ZeroDivisionError"
        if score == 4.2 and empty_score == 0.0:
            print("[7/7] Средний балл считается верно, пустой список не роняет программу")
            passed += 1
        elif score != 4.2:
            print(f"[7/7] Ошибка: для [5, 4, 5, 3, 4] ожидалось 4.2, получено {score}")
        else:
            print(f"[7/7] Ошибка: для пустого списка [] ожидалось 0.0, получено {empty_score}")

    if passed == total_tests:
        print(f"Все тесты пройдены успешно ({passed}/{total_tests}). Можно делать коммит и пуш в GitHub")
    else:
        print(f"Пройдено тестов: {passed}/{total_tests}. Поправь код в roulette.py и запусти снова.")


if __name__ == "__main__":
    run_tests()