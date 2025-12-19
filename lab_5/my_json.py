import logging
from json import load
from typing import Any

logger = logging.getLogger(__name__)


def read_json(filename: str) -> dict[str, Any]:
    """
    Читает и парсит JSON-файл с корректной кодировкой.

    Args:
        filename: Путь к JSON-файлу для чтения.

    Returns:
        Словарь с данными из JSON-файла.

    Raises:
        FileNotFoundError: Если указанный файл не существует.
        json.JSONDecodeError: Если файл содержит некорректный JSON.

    Example:
        >>> data = read_json("settings.json")
        >>> print(data["access_token"])
        'ваш_токен_доступа'

    Note:
        Использует кодировку utf-8-sig для корректной обработки BOM.
    """
    logger.debug(f"Чтение JSON файла: {filename}")

    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            data = load(file)
        
        logger.info(f"JSON файл успешно прочитан: {filename}, ключи: {list(data.keys())}")
        return data
        
    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {filename}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON в файле {filename}: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении {filename}: {e}")
        raise