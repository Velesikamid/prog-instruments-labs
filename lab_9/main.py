import os
import sys
from typing import Any, Optional

from config_manager import get_config, get_config_value
from logging_config import setup_logging
from settings_manager import get_settings, get_setting
from filemanager import write_to_file
from list_of_people import get_list_of_people
from parser import Parser

setup_logging()

import logging
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Основная функция программы для парсинга и обработки комментариев ВКонтакте.
    """
    try:
        config = get_config()
        env = get_config_value("env", "dev")
        
        logger.info(f"Запуск программы в режиме: {env}")
        logger.debug(f"Конфигурация загружена: {config.app.name} v{config.app.version}")
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        env = "dev"
    
    try:
        logger.info("Загрузка настроек")
        settings = get_settings()
        
        if not settings.get("access_token"):
            logger.warning("VK API токен не найден в настройках")
            print("\nВнимание: VK API токен не найден!")
            print("Добавьте его в settings.json или установите переменную окружения VK_ACCESS_TOKEN")
        
        logger.info("Инициализация парсера VK")
        parser = Parser(settings)
        
        logger.info("Загрузка комментариев из VK")
        comments: list[str] = parser.get_comments()
        
        if not comments:
            print("\nНе удалось загрузить комментарии или они отсутствуют.")
            return 1
        
        try:
            default_search = get_config_value("list_of_people.default_is_students", False)
        except:
            default_search = False
            
        search_prompt = f"Кого ищем (0 - нестудентов, 1 - студентов)? [по умолчанию: {int(default_search)}]: "
        search_type = input(search_prompt).strip()
        
        if not search_type:
            is_students = default_search
        else:
            is_students = bool(int(search_type))
        
        logger.info(f"Тип поиска: {'студенты' if is_students else 'не-студенты'}")
        
        try:
            pattern = get_config_value("list_of_people.pattern", 
                r"\d{4}[-–]\d{2}.?\d{2}.?\d{2}[a-zа-я]?")
        except:
            pattern = r"\d{4}[-–]\d{2}.?\d{2}.?\d{2}[a-zа-я]?"
        
        logger.info("Фильтрация и обработка людей")
        filtered_comments: list[str] = get_list_of_people(
            comments,
            settings["blacklist"],
            is_students,
            pattern=pattern
        )
        
        if not filtered_comments:
            print("\nНе найдено ни одного человека по заданным критериям.")
            return 0
        
        try:
            default_output_dir = get_config_value("paths.output_dir", "results")
            default_output_file = get_config_value("paths.default_output", "output.txt")
        except:
            default_output_dir = "results"
            default_output_file = "output.txt"
            
        default_path = f"{default_output_dir}/{default_output_file}"
        
        path_prompt = f"Введите путь к файлу, куда сохранить результат [по умолчанию: {default_path}]: "
        output_path = input(path_prompt).strip()
        
        if not output_path:
            output_path = default_path
        
        logger.info(f"Путь для сохранения: {output_path}")
        
        try:
            create_dirs = get_config_value("filemanager.create_dirs", True)
            overwrite = get_config_value("filemanager.overwrite", True)
        except:
            create_dirs = True
            overwrite = True
        
        logger.info(f"Сохранение {len(filtered_comments)} записей в файл")
        path_to_result: Optional[str] = write_to_file(
            filtered_comments, 
            output_path,
            create_dirs=create_dirs,
            overwrite=overwrite
        )
        
        print(f"\n{'='*50}")
        print(f"Результаты:")
        print(f"Количество человек: {len(filtered_comments)}")
        print(f"Список записан в: {path_to_result}")
        print(f"{'='*50}\n")
        
        logger.info(f"Программа успешно завершена. Сохранено: {len(filtered_comments)} записей")
        
    except KeyboardInterrupt:
        logger.warning("Программа прервана пользователем")
        print("\nПрограмма прервана.")
        return 130
    except Exception as exc:
        logger.critical(f"Критическая ошибка в программе: {exc}", exc_info=True)
        print(f"\nОшибка: {exc}")
        
        try:
            if get_config_value("dev.debug", False):
                import traceback
                traceback.print_exc()
        except:
            pass
        
        return 1
    
    return 0


if __name__ == "__main__":
    # Можно указать режим через переменную окружения
    # export APP_ENV=prod
    # или через аргумент командной строки
    if len(sys.argv) > 1 and sys.argv[1] in ("dev", "prod"):
        os.environ["APP_ENV"] = sys.argv[1]
    
    exit_code = main()
    sys.exit(exit_code)