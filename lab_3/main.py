import os.path
import re

import requests


def get_ids() -> list[str]:
    """
    Извлекает из ссылки на обсуждение group_id и topic_id.

    Raises:
        ValueError: Выбрасывается, если не удалось найти group_id и topic_id

    Returns:
        list[str]: Список, содержащий group_id и topic_id
    """
    topic_url = input("Введите ссылку на обсуждение: ")
    pattern = r"-\d+_\d+"
    ids = re.search(pattern, topic_url)

    if ids:
        return ids.group()[1:].split("_")
    else:
        raise ValueError(
            "Не удалось получить доступ к обсуждению! "
            "Вероятно, вы ввели неправильную ссылку."
        )


def get_number_of_comments(url: str, params: dict) -> int:
    """
    Возвращает количество сообщений в обсуждении.

    Args:
        url (str): get-запрос к API ВК
        params (dict): параметры get-запроса

    Returns:
        int: Количество сообщений в обсуждении
    """
    params["count"] = 1
    response = requests.get(url, params).json()

    return response["response"]["count"]


def get_comments(
    url: str, params: dict, count: int, number_of_comments: int
) -> list[str]:
    """
    Возвращает список сообщений из обсуждения.

    Args:
        url (str): get-запрос к API ВК
        params (dict): Параметры get-запроса
        count (int): Максимальное количество возвращаемых сообщений (<= 100)
        number_of_comments (int): Количество сообщений в обсуждении

    Returns:
        list[str]: Список сообщений из обсуждения
    """
    params["count"] = count
    comments = []

    while len(comments) < number_of_comments:
        response = requests.get(url, params).json()
        comments.extend(response["response"]["items"])
        params["offset"] += count

    return [i["text"] for i in comments]


def get_students(comments: list[str]) -> list[str]:
    """
    Возвращает сообщения тех, кто указал группу (студенты СУ).

    Args:
        comments (list[str]): Список всех сообщений

    Returns:
        list[str]: Список сообщений студентов
    """
    pattern = r"\d{4}[-–]\d{2}.?\d{2}.?\d{2}[a-zа-я]?"
    temp = [i.lower() for i in comments if re.search(pattern, i)]
    temp = temp[1:]
    result = []
    for i in temp:
        group = re.search(pattern, i).group().strip()
        student = re.sub(pattern, "", i).strip()
        student = re.sub(r"\d[.)]", "", student).strip()
        student = re.sub("\n", " ", student).strip()
        result.append(student + " " + group)
    result = list(set(result))

    return result


def sort_students(comments: list[str]) -> list[str]:
    """
    Сортирует сообщения по алфавиту.

    Args:
        comments (list[str]): Список, который необходимо отсортировать

    Returns:
        list[str]: Отсортированный список
    """
    alphabet = "жзийклмнопрстуфхцчшщъыьэюя"
    problems = []

    n = len(comments)
    i = 0
    while i < n:
        if comments[i][0] == "ё":
            problems.append(comments.pop(i))
            i -= 1
            n -= 1
        i += 1

    comments.sort()
    problems.sort()

    for i in range(len(comments)):
        if comments[i][0] in alphabet:
            comments[i:i] = problems
            break

    return [comment.title() for comment in comments]


def delete_cringe(comments: list[str], cringe: list[str]) -> list[str]:
    """
    Удаляет из comments все элементы, перечисленные в cringe.

    Args:
        comments (list[str]): Исходный список
        cringe (list[str]): "Чёрный список" элементов

    Returns:
        list[str]: Полученный список
    """
    result = [comment for comment in comments if comment not in cringe]
    for word in cringe:
        result = [re.sub(word, "", comment).strip() for comment in result]

    return result


def write_to_file(comments: list[str], path: str) -> str:
    """
    Записывает список строк в файл.

    Args:
        comments (list[str]): Список на запись
        path (str): Путь к файлу, куда записывать

    Returns:
        str: Путь к файлу, куда была произведена запись
    """
    path_to_file, filename = os.path.split(path)
    if not os.path.exists(path_to_file):
        path = filename

    with open(path, "w", encoding="utf-8") as file:
        for comment in comments:
            file.write(comment)
            file.write("\n")

    return os.path.realpath(filename)


def main() -> int:
    """
    Основная программа.

    Returns:
        int: Код завершения (0 - успех, 1 - ошибка)
    """
    cringe = [
        "Самарский Университет",
        "Сгспу",
        "Сниу",
        "Группа",
        "Им. Королёва",
        "Самарский Государственный Университет",
    ]
    access_token = (
        "5ccf39195ccf39195ccf3919b15fd0d35d55ccf5ccf39193bcf1b3c96d8f575bf1814888"
    )
    v = 5.199
    count = 100
    offset = 0
    try:
        group_id, topic_id = get_ids()
    except ValueError as exc:
        print("Ошибка:", exc)

        return 1

    url = "https://api.vk.com/method/board.getComments"
    params = {
        "access_token": access_token,
        "v": v,
        "group_id": group_id,
        "topic_id": topic_id,
        "offset": offset,
    }
    try:
        number_of_comments = get_number_of_comments(url, params)
        comments = get_comments(url, params, count, number_of_comments)
    except BaseException as exc:
        print(
            "Ошибка: Не удалось загрузить комментарии! "
            "Проверьте подключение к интернету."
        )

        return 1

    comments = get_students(comments)
    comments = sort_students(comments)
    comments = delete_cringe(comments, cringe)
    try:
        path_to_result = write_to_file(
            comments, input("Введите путь к файлу," " куда записать результат: ")
        )
    except IsADirectoryError as exc:
        print(f"Ошибка: {exc}. Укажите имя файла!")

        return 1

    print(
        f"Количество студентов: {len(comments)}.",
        f"Их список записан в {path_to_result}",
        sep="\n",
    )

    return 0


if __name__ == "__main__":
    restart = 1
    while restart:
        restart = main()
