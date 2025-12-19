import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def delete_trash(comments: list[str], blacklist: list[str]) -> list[str]:
    """
    Очищает комментарии от нежелательных слов и форматирует их.

    Удаляет из каждого комментария слова из черного списка,
    обрезает пробелы и приводит первый символ каждого слова к заглавной букве.

    Args:
        comments: Список строк (комментариев) для обработки.
        blacklist: Список слов и выражений для удаления.

    Returns:
        Очищенный и отформатированный список комментариев.

    Example:
        >>> comments = ["иван иванов спам", "мария петрова"]
        >>> blacklist = ["спам"]
        >>> delete_trash(comments, blacklist)
        ['Иван Иванов', 'Мария Петрова']
    """
    logger.debug(f"Очистка комментариев. Исходно: {len(comments)}, стоп-слов: {len(blacklist)}")

    if not comments:
        logger.warning("Получен пустой список комментариев для очистки")
        return []
    
    original_count = len(comments)

    for word in blacklist:
        comments = [re.sub(word, "", comment).strip() for comment in comments]
    
    cleaned_comments = [i.title() for i in comments if i not in blacklist]
    logger.debug(f"Очистка завершена. Осталось: {len(cleaned_comments)} из {original_count}")
    
    return cleaned_comments


def get_list_of_people(
    comments: list[str],
    blacklist: list[str],
    is_students: bool = False,
    pattern: str = r"\d{4}[-–]\d{2}.?\d{2}.?\d{2}[a-zа-я]?",
) -> list[str]:
    """
    Фильтрует и обрабатывает список людей из комментариев.

    Разделяет комментарии на студентов и не-студентов на основе
    наличия шаблона номера группы, очищает от мусора и возвращает
    уникальный отсортированный список.

    Args:
        comments: Список исходных комментариев.
        blacklist: Список слов для удаления при очистке.
        is_students: Если True, ищет студентов (с номером группы),
                     если False — не-студентов (без номера группы).
        pattern: Регулярное выражение для поиска номера группы
                 (формат: ГГГГ-ББ.ББ.ББ[доп]).

    Returns:
        Уникальный отсортированный список имен людей.

    Example:
        >>> comments = ["иван иванов 2021-01.02.03", "мария петрова"]
        >>> blacklist = []
        >>> # Поиск студентов
        >>> get_list_of_people(comments, blacklist, is_students=True)
        ['Иван Иванов 2021-01.02.03']
        >>> # Поиск не-студентов
        >>> get_list_of_people(comments, blacklist, is_students=False)
        ['Мария Петрова']

    Note:
        - Все комментарии приводятся к нижнему регистру перед обработкой.
        - Для студентов номер группы добавляется к имени через пробел.
        - Возвращаются только уникальные значения в алфавитном порядке.
    """
    logger.info(f"Поиск {'студентов' if is_students else 'не-студентов'}. "
                f"Комментариев: {len(comments)}, паттерн: {pattern}")

    if not comments:
        logger.warning("Получен пустой список комментариев для фильтрации")
        return []

    comments = [i.lower() for i in comments]
    logger.debug(f"Приведено к нижнему регистру: {len(comments)} комментариев")

    temp = (
        [i for i in comments if re.search(pattern, i)]
        if is_students
        else [i for i in comments if not re.search(pattern, i)]
    )

    logger.debug(f"После фильтрации по паттерну: {len(temp)} комментариев")

    result: list[str] = []
    for i in temp:
        group: Optional[str] = (
            re.search(pattern, i).group().strip() if is_students else None
        )
        people: str = re.sub(pattern, "", i).strip()
        result.append(f"{people} {group}" if is_students else people)
    
    result = delete_trash(result, blacklist)
    
    unique_result = sorted(list(set(result)))
    
    logger.info(f"Найдено уникальных {'студентов' if is_students else 'не-студентов'}: "
                f"{len(unique_result)}")
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Первые 5 результатов: {unique_result[:5]}")
    
    return unique_result
