from typing import Any, Optional

from filemanager import write_to_file
from list_of_people import get_list_of_people
from my_json import read_json
from parser import Parser


def main() -> int:
    """
    Основная функция программы для парсинга и обработки комментариев ВКонтакте.

    Программа выполняет последовательно:
    1. Чтение настроек из JSON-файла
    2. Инициализацию парсера и получение комментариев
    3. Фильтрацию людей (студентов или не-студентов)
    4. Сохранение результатов в файл

    Returns:
        Код завершения программы: 0 при успехе, 1 при ошибке.

    Example:
        >>> # Запуск из командной строки
        >>> python main.py
        Введите ссылку на обсуждение: https://vk.com/topic-123456_7890123
        Кого ищем (0 - нестудентов, 1 - студентов)? 1
        Введите путь к файлу, куда сохранить результат: results/students.txt
        Количество человек: 42.
        Их список записан в /full/path/results/students.txt

    Note:
        - Для работы требуется файл settings.json с токеном доступа VK API.
        - При возникновении любой ошибки программа выводит её и завершается.
    """
    try:
        settings: dict[str, Any] = read_json("settings.json")
        parser = Parser(settings)
        comments: list[str] = parser.get_comments()
        comments: list[str] = get_list_of_people(
            comments,
            settings["blacklist"],
            bool(int(input("Кого ищем (0 - нестудентов, 1 - студентов)? "))),
        )
        path_to_result: Optional[str] = write_to_file(
            comments, input("Введите путь к файлу, куда сохранить результат: ")
        )
        print(
            f"Количество человек: {len(comments)}.",
            f"Их список записан в {path_to_result}",
            sep="\n",
        )
    except Exception as exc:
        print(f"Ошибка: {exc}")

    return 0


if __name__ == "__main__":
    main()
