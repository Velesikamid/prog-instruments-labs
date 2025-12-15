import re
from typing import Any

import requests


class Parser:
    """
    Парсер для получения комментариев из обсуждений ВКонтакте через API.

    Класс предоставляет методы для извлечения идентификаторов из URL,
    получения количества комментариев и загрузки всех сообщений из обсуждения.

    Attributes:
        __url (str): URL эндпоинта API ВКонтакте для получения комментариев.
        __params (Dict[str, Any]): Параметры запроса к API.
        __number_of_comments (int): Общее количество комментариев в обсуждении.
    """

    def __init__(self, settings: dict[str, Any]) -> None:
        """
        Инициализирует парсер с настройками API.

        Args:
            settings: Словарь с настройками для доступа к API ВКонтакте.
                      Должен содержать ключи: access_token, v, offset.

        Example:
            >>> settings = {
            ...     "access_token": "ваш_токен",
            ...     "v": "5.131",
            ...     "offset": 0
            ... }
            >>> parser = Parser(settings)
        """
        self.__url: str = "https://api.vk.com/method/board.getComments"
        self.__params: dict[str, Any] = {
            "access_token": settings["access_token"],
            "v": settings["v"],
            "group_id": 0,
            "topic_id": 0,
            "offset": settings["offset"],
            "count": 1,
        }
        self.get_ids(input("Введите ссылку на обсуждение: "))
        self.__number_of_comments: int = 0

    def get_ids(self, topic_url: str, pattern: str = r"-\d+_\d+") -> None:
        """
        Извлекает из ссылки на обсуждение group_id и topic_id.

        Метод парсит URL обсуждения ВКонтакте и извлекает идентификаторы
        группы и топика для последующих API-запросов.

        Args:
            topic_url: Полная ссылка на обсуждение ВКонтакте.
            pattern: Регулярное выражение для поиска ID (по умолчанию
                     ищет паттерн типа "-123456_7890123").

        Raises:
            ValueError: Если не удалось найти group_id и topic_id в ссылке.

        Example:
            >>> parser = Parser(settings)
            >>> parser.get_ids("https://vk.com/topic-123456_7890123")
            # Устанавливает group_id=123456, topic_id=7890123
        """
        ids = re.search(pattern, topic_url)

        if ids:
            self.__params["group_id"], self.__params["topic_id"] = ids.group()[
                1:
            ].split("_")
        else:
            raise ValueError(
                "Не удалось получить доступ к обсуждению! "
                "Вероятно, вы ввели неправильную ссылку."
            )

    def get_number_of_comments(self) -> None:
        """
        Получает общее количество сообщений в обсуждении.

        Выполняет запрос к API ВКонтакте для получения информации
        о количестве комментариев в указанном обсуждении.

        Note:
            Обновляет внутренний атрибут __number_of_comments.
        """
        self.__number_of_comments = requests.get(self.__url, self.__params).json()[
            "response"
        ]["count"]

    def get_comments(self) -> list[str]:
        """
        Возвращает список всех сообщений из обсуждения.

        Загружает все комментарии из обсуждения, выполняя несколько
        запросов к API (по 100 сообщений за запрос).

        Returns:
            Список текстов сообщений из обсуждения. Первое сообщение
            (тема обсуждения) исключается из результатов.

        Example:
            >>> comments = parser.get_comments()
            >>> print(f"Загружено {len(comments)} комментариев")
            >>> for comment in comments[:3]:
            ...     print(comment)
        """
        self.get_number_of_comments()
        self.__params["count"] = 100
        comments: list[dict[str, Any]] = []

        while len(comments) < self.__number_of_comments:
            comments.extend(
                requests.get(self.__url, self.__params).json()["response"]["items"]
            )
            self.__params["offset"] += self.__params["count"]

        return [i["text"] for i in comments[1:]]
