import sys
from typing import Any, Optional

from logging_config import setup_logging
from filemanager import write_to_file
from list_of_people import get_list_of_people
from my_json import read_json
from parser import Parser

setup_logging(log_level="INFO", log_to_file=True)

import logging
logger = logging.getLogger(__name__)


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
    logger.info("Запуск программы")

    try:
        logger.info("Чтение настроек из settings.json")
        settings: dict[str, Any] = read_json("settings.json")

        logger.info("Инициализация парсера VK")
        parser = Parser(settings)

        logger.info("Загрузка комментариев из VK")
        comments: list[str] = parser.get_comments()

        search_type = input("Кого ищем (0 - нестудентов, 1 - студентов)? ")
        is_students = bool(int(search_type))
        logger.info(f"Тип поиска: {'студенты' if is_students else 'не-студенты'}")
        
        logger.info("Фильтрация и обработка людей")
        filtered_comments: list[str] = get_list_of_people(
            comments,
            settings["blacklist"],
            is_students,
        )
        
        output_path = input("Введите путь к файлу, куда сохранить результат: ")
        logger.info(f"Путь для сохранения: {output_path}")
        
        logger.info(f"Сохранение {len(filtered_comments)} записей в файл")
        path_to_result: Optional[str] = write_to_file(
            filtered_comments, 
            output_path,
            create_dirs=True,
            overwrite=True
        )
        
        logger.info(f"Программа успешно завершена. Сохранено: {len(filtered_comments)} записей")
        
    except KeyboardInterrupt:
        logger.warning("Программа прервана пользователем")
        print("\nПрограмма прервана.")
        return 130
    except Exception as exc:
        logger.critical(f"Критическая ошибка в программе: {exc}", exc_info=True)
        print(f"Ошибка: {exc}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
