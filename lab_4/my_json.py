from json import load
from typing import Any

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
    with open(filename, "r", encoding="utf-8-sig") as file:
        return load(file)
