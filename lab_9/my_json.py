import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def read_json(filename: str) -> dict[str, Any]:
    """
    Читает и парсит JSON-файл с корректной кодировкой.
    """
    logger.debug(f"Чтение JSON файла: {filename}")
    
    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        
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