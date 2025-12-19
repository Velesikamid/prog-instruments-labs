import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def write_to_file(
    comments: list[str],
    path: str,
    create_dirs: bool = True,
    overwrite: bool = True
) -> Optional[str]:
    """
    Записывает список комментариев в файл,
    создавая директории при необходимости.

    Args:
        comments: Список строк для записи в файл.
        path: Полный путь к файлу (включая имя файла и расширение).
        create_dirs: Если True, создает недостающие директории в пути.
        overwrite: Если True, перезаписывает существующий файл.
                   Если False и файл существует — вызывает исключение.

    Returns:
        Абсолютный путь к записанному файлу в случае успеха.
        None в случае критической ошибки (не реализовано в текущей версии).

    Raises:
        ValueError: Если путь не содержит имени файла.
        FileNotFoundError: Если директория не существует и create_dirs=False.
        FileExistsError: Если файл уже существует и overwrite=False.
        PermissionError: Если нет прав на запись в указанную директорию.
        OSError: При других ошибках файловой системы.

    Example:
        >>> comments = ["Иван Иванов", "Мария Петрова"]
        >>> write_to_file(comments, "results/people.txt")
        '/home/user/project/results/people.txt'

    Note:
        - Каждый комментарий записывается с новой строки.
        - Файл сохраняется в кодировке UTF-8.
    """
    logger.debug(f"Начало записи в файл. Путь: {path}, комментариев: {len(comments)}")

    normalized_path = os.path.normpath(path)
    dir_path, filename = os.path.split(normalized_path)

    if not filename:
        logger.error(f"Путь не содержит имени файла: {path}")
        raise ValueError("Путь должен содержать имя файла")
    
    logger.debug(f"Нормализованный путь: {normalized_path}, директория: {dir_path}, файл: {filename}")

    if dir_path and not os.path.exists(dir_path):
        if create_dirs:
            logger.info(f"Создание директории: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
        else:
            logger.error(f"Директория не существует: {dir_path}")
            raise FileNotFoundError(
                f"Директория не существует: {dir_path}. "
                "Используйте create_dirs=True для автоматического создания"
            )
    
    full_path = os.path.join(dir_path, filename) if dir_path else filename

    if os.path.exists(full_path):
        if not overwrite:
            logger.error(f"Файл уже существует: {full_path}")
            raise FileExistsError(f"Файл уже существует: {full_path}")
        else:
            logger.warning(f"Файл будет перезаписан: {full_path}")
    
    try:
        logger.debug(f"Запись {len(comments)} комментариев в файл: {full_path}")
        with open(full_path, "w", encoding="utf-8") as file:
            for i, comment in enumerate(comments):
                if i > 0:
                    file.write("\n")
                file.write(comment)
        
        absolute_path = os.path.abspath(full_path)
        logger.info(f"Файл успешно записан: {absolute_path}, записано строк: {len(comments)}")
        return absolute_path
        
    except PermissionError as e:
        logger.critical(f"Нет прав на запись в файл: {full_path}. Ошибка: {e}")
        raise
    except OSError as e:
        logger.critical(f"Ошибка файловой системы при записи в {full_path}. Ошибка: {e}")
        raise
