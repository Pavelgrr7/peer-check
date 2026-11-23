"""
Тестовый сценарий для проверки модуля roulette.py
Запуск: python test_roulette.py
"""
import os
import sys

try:
    import roulette
    from roulette import select_lab_for_review, validate_review
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедись, что функции select_lab_for_review и validate_review объявлены в roulette.py")
    sys.exit(1)


def run_tests():
    total_tests = 10
    passed = 0

    print("Запуск проверки бизнес-логики (roulette.py)...")

    # Тест 1: Исключение своей работы
    mock_labs = [
        {"id": 1, "student_token": "egor", "lab_number": 1},
        {"id": 2, "student_token": "kirill", "lab_number": 1},
    ]
    chosen = select_lab_for_review("egor", mock_labs)
    if chosen and chosen["student_token"] != "egor":
        print("[1/10] Алгоритм не выдает студенту его собственную работу")
        passed += 1
    else:
        print("[1/10] Ошибка: алгоритм вернул работу самого пользователя!")

    # Тест 2: Пустая очередь / нет чужих работ
    only_own_labs = [{"id": 1, "student_token": "egor", "lab_number": 1}]
    chosen_empty = select_lab_for_review("egor", only_own_labs)
    if chosen_empty is None:
        print("[2/10] Возврат None, если доступных чужих работ нет")
        passed += 1
    else:
        print("[2/10] Ошибка: если доступных работ нет, функция должна возвращать None")

    # Тест 3: Корректный отзыв проходит валидацию
    valid_ratings = [5, 4, 5, 4, 5]
    good_comment = "Код написан аккуратно, переменные названы понятно. Добавлены скриншоты тестов."
    is_ok, msg = validate_review(valid_ratings, good_comment)
    if is_ok is True:
        print("[3/10] Качественный отзыв успешно проходит валидацию")
        passed += 1
    else:
        print(f"[3/10] Ошибка: корректный отзыв был отклонен ({msg})")

    # Тест 4: Слишком короткий отзыв блокируется
    is_ok, msg = validate_review([5, 5, 5, 5, 5], "все ок норм")
    if is_ok is False:
        print("[4/10] Защита от коротких отписок (< 50 символов) работает")
        passed += 1
    else:
        print("[4/10] Ошибка: валидатор пропустил короткую отписку!")

    # Тест 5: Некорректные оценки
    is_ok_ratings, _ = validate_review([5, 4], good_comment) # мало оценок
    is_ok_range, _ = validate_review([6, 5, 4, 3, 2], good_comment) # оценка 6
    if is_ok_ratings is False and is_ok_range is False:
        print("[5/10] Проверка списка оценок (строго 5 чисел от 1 до 5) работает")
        passed += 1
    else:
        print("[5/10] Ошибка: валидатор пропустил неверное количество оценок или значения вне [1..5]")

    # Тест 6: Формат псевдонима "Слово Слово #123" (задача #13)
    generate_pseudonym = getattr(roulette, "generate_pseudonym", None)
    if generate_pseudonym is None:
        print("[6/10] Функция generate_pseudonym ещё не написана (задача #13)")
    else:
        pseudonym = generate_pseudonym()
        parts = pseudonym.split(" #") if isinstance(pseudonym, str) else []
        if (len(parts) == 2 and len(parts[0].split()) == 2
                and parts[1].isdigit() and 100 <= int(parts[1]) <= 999):
            print(f"[6/10] Псевдоним в нужном формате: {pseudonym}")
            passed += 1
        else:
            print(f"[6/10] Ошибка: псевдоним '{pseudonym}' не в формате 'Слово Слово #123' (число от 100 до 999)")

    # Тест 7: Средний балл и защита от пустого списка (задача #13)
    calculate_final_score = getattr(roulette, "calculate_final_score", None)
    if calculate_final_score is None:
        print("[7/10] Функция calculate_final_score ещё не написана (задача #13)")
    else:
        score = calculate_final_score([5, 4, 5, 3, 4])
        try:
            empty_score = calculate_final_score([])
        except ZeroDivisionError:
            empty_score = "ошибка ZeroDivisionError"
        if score == 4.2 and empty_score == 0.0:
            print("[7/10] Средний балл считается верно, пустой список не роняет программу")
            passed += 1
        elif score != 4.2:
            print(f"[7/10] Ошибка: для [5, 4, 5, 3, 4] ожидалось 4.2, получено {score}")
        else:
            print(f"[7/10] Ошибка: для пустого списка [] ожидалось 0.0, получено {empty_score}")

    # Тест 8: Проверка формы регистрации (задача «Регистрация и пароли в логике»)
    validate_registration = getattr(roulette, "validate_registration", None)
    if validate_registration is None:
        print("[8/10] Функция validate_registration ещё не написана (задача «Регистрация и пароли в логике»)")
    else:
        good, _ = validate_registration("student@tpu.ru", "qwerty123")
        no_at, _ = validate_registration("student.tpu.ru", "qwerty123")
        short, _ = validate_registration("student@tpu.ru", "123")
        if good is True and no_at is False and short is False:
            print("[8/10] Форма регистрации проверяется: почта с @ и точкой, пароль от 8 символов")
            passed += 1
        elif good is not True:
            print("[8/10] Ошибка: правильные почта и пароль ('student@tpu.ru', 'qwerty123') отклонены")
        elif no_at is not False:
            print("[8/10] Ошибка: пропущена почта без @ ('student.tpu.ru')")
        else:
            print("[8/10] Ошибка: пропущен пароль короче 8 символов ('123')")

    # Тест 9: Хеш пароля с солью (задача «Регистрация и пароли в логике»)
    hash_password = getattr(roulette, "hash_password", None)
    check_password = getattr(roulette, "check_password", None)
    if hash_password is None or check_password is None:
        print("[9/10] Функции hash_password и check_password ещё не написаны (задача «Регистрация и пароли в логике»)")
    else:
        stored = hash_password("qwerty123")
        if "qwerty123" in stored:
            print("[9/10] Ошибка: пароль виден в хеше в открытом виде")
        elif hash_password("qwerty123") == stored:
            print("[9/10] Ошибка: одинаковые пароли дают одинаковый хеш, нужна случайная соль")
        elif check_password("qwerty123", stored) is not True:
            print("[9/10] Ошибка: check_password не узнал правильный пароль")
        elif check_password("qwerty124", stored) is not False:
            print("[9/10] Ошибка: check_password пропустил неправильный пароль")
        else:
            print("[9/10] Пароль хранится хешем с солью, проверка входа работает")
            passed += 1

    # Тест 10: Имя PDF на диске придумывает система (задача «Регистрация и пароли в логике»)
    save_uploaded_pdf = getattr(roulette, "save_uploaded_pdf", None)
    if save_uploaded_pdf is None:
        print("[10/10] Функция save_uploaded_pdf не найдена в roulette.py")
    else:
        path1 = save_uploaded_pdf(b"%PDF-1.4 first", "Ivanov_lab1.pdf")
        path2 = save_uploaded_pdf(b"%PDF-1.4 second", "Ivanov_lab1.pdf")
        saved_in_uploads = (os.path.dirname(path1) == "uploads" and os.path.dirname(path2) == "uploads"
                            and os.path.exists(path1) and os.path.exists(path2))
        if path1 == path2:
            print("[10/10] Ошибка: два файла с одинаковым именем записались в один путь, второй затёр первый. "
                  "Имя файла должна придумывать функция")
        elif "Ivanov" in path1:
            print(f"[10/10] Ошибка: в пути '{path1}' осталось исходное имя файла, по нему можно узнать автора")
        elif not saved_in_uploads:
            print(f"[10/10] Ошибка: файлы должны лежать в папке uploads, получено '{path1}' и '{path2}'")
        else:
            print(f"[10/10] PDF сохраняется в uploads под системным именем: {path1}")
            passed += 1
        # убираем тестовые файлы за собой
        for path in (path1, path2):
            if os.path.exists(path):
                os.remove(path)

    if passed == total_tests:
        print(f"Все тесты пройдены успешно ({passed}/{total_tests}). Можно делать коммит и пуш в GitHub")
    else:
        print(f"Пройдено тестов: {passed}/{total_tests}. Поправь код в roulette.py и запусти снова.")


if __name__ == "__main__":
    run_tests()