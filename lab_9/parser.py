import re
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


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
        logger.info("Инициализация парсера VK API")

        self.__url: str = "https://api.vk.com/method/board.getComments"
        self.__params: dict[str, Any] = {
            "access_token": settings["access_token"],
            "v": settings["v"],
            "group_id": 0,
            "topic_id": 0,
            "offset": settings["offset"],
            "count": 1,
        }

        if not self.__params["access_token"]:
            logger.error("Отсутствует access_token в настройках")
            raise ValueError("Требуется access_token для работы с VK API")
        
        logger.debug(f"Параметры инициализированы: v={self.__params['v']}, "
                    f"offset={self.__params['offset']}")

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
        logger.debug(f"Парсинг URL: {topic_url}")

        ids = re.search(pattern, topic_url)

        if ids:
            group_id, topic_id = ids.group()[1:].split("_")
            self.__params["group_id"] = group_id
            self.__params["topic_id"] = topic_id
            logger.info(f"Извлечены ID: group_id={group_id}, topic_id={topic_id}")
        else:
            logger.error(f"Не удалось извлечь ID из URL: {topic_url}")
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
        logger.debug("Запрос количества комментариев")

        try:
            response = requests.get(self.__url, self.__params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                error_msg = data["error"].get("error_msg", "Неизвестная ошибка")
                logger.error(f"Ошибка VK API: {error_msg}")
                raise RuntimeError(f"Ошибка VK API: {error_msg}")
            
            self.__number_of_comments = data["response"]["count"]
            logger.info(f"Общее количество комментариев: {self.__number_of_comments}")
            
        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе количества комментариев")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при запросе количества комментариев: {e}")
            raise

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
        logger.info("Начало загрузки комментариев")

        self.get_number_of_comments()

        if self.__number_of_comments == 0:
            logger.warning("В обсуждении нет комментариев")
            return []

        self.__params["count"] = 100
        comments: list[dict[str, Any]] = []

        total_requests = (self.__number_of_comments // 100) + 1
        logger.info(f"Потребуется запросов: {total_requests}")

        try:
            while len(comments) < self.__number_of_comments:
                current_offset = self.__params["offset"]
                loaded = len(comments)
                logger.debug(f"Запрос комментариев [{loaded}/{self.__number_of_comments}], "
                           f"offset: {current_offset}")
                
                response = requests.get(self.__url, self.__params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if "error" in data:
                    error_msg = data["error"].get("error_msg", "Неизвестная ошибка")
                    logger.error(f"Ошибка VK API при загрузке комментариев: {error_msg}")
                    break
                
                batch_comments = data["response"]["items"]
                comments.extend(batch_comments)
                
                self.__params["offset"] += self.__params["count"]
            
            result = [i["text"] for i in comments[1:]]
            logger.info(f"Загружено комментариев: {len(result)}")
            
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Первые 3 комментария: {result[:3]}")
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Таймаут при загрузке комментариев")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при загрузке комментариев: {e}")
            raise