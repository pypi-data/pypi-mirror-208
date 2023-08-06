"""Базовые функции для получения страниц и парсинга."""
from asyncio import sleep
from hashlib import sha256
from time import time

from selectolax.lexbor import LexborHTMLParser

from pyaklass.const import BASE_URL
from pyaklass.exc import PossibleIPBlockError, PyaklassError


def get_captcha_answer(salt: str, target_hash: str) -> int:
    """Получить решение капчи.

    Args:
        salt (str): Соль
        target_hash (str): SHA256 ответа

    Returns:
        int: Решение или 0 в случае провала
    """
    for i in range(0, int(2e5) + 1):
        computed_hash = sha256(f'{i}{salt}{i}'.encode('utf-8'))
        if computed_hash.hexdigest() == target_hash:
            return i

    return 0


async def check_limiter(lock, limiter):
    """Проверить ограничитель.

    Args:
        lock (Lock): Синхронизатор для ограничителя
        limiter (dict): Ограничитель
    """
    with lock:
        value = limiter.value
        if value['current'] >= value['amount']:
            await sleep(value['seconds'])
            value['current'] = 1
        elif time() - (value.get('last_check', 0) + value['seconds'] + 1) >= 1:
            value['current'] = 1
        else:
            value['current'] += 1
        value['last_check'] = time()
        limiter.set(value)


async def solve_captcha(client, limiter: tuple, params) -> str:
    """Решить капчу.

    Args:
        client (httpx.AsyncClient): Клиент
        limiter (tuple): Ограничитель и его синхронизатор
        params (httpx.QueryParams): GET-параметры для решения капчи

    Returns:
        str: Текст HTML-страницы, указанной в `params['returnUrl']`

    Raises:
        PyaklassError: Невозможно решить капчу
    """
    answer = get_captcha_answer(params['base'], params['target'])
    if answer == 0:
        raise PyaklassError(f'Невозможно решить капчу: "{params}".')

    payload = {
        'r': params['returnUrl'],
        'b': params['base'],
        's': answer,
        'tn': 0,  # Try Number (Amount of attempts)
    }
    await check_limiter(*limiter)
    resp = await client.post(f'{BASE_URL}/Account/DoSolveCaptcha1', data=payload)

    if 'SolveCaptcha' in resp.url.path:
        raise PyaklassError(f'Невозможно решить капчу: "{params}".')
    return resp.text


async def fetch(client, limiter: tuple, url: str):
    """Получить текст по указанному URL адресу.

    Args:
        client (httpx.AsyncClient): Клиент
        limiter (tuple): Ограничитель и его синхронизатор
        url (str): Путь для URL: `https://www.yaklass.ru/{url}`

    Returns:
        Union[str, None]: HTML-страница или None в случае 302 (Работа еще проверяется)

    Raises:
        PossibleIPBlockError: Ошибка при возможной блокировке IP сервисом
        PyaklassError: Ошибка при выполении запроса
    """
    await check_limiter(*limiter)
    resp = await client.get(f'{BASE_URL}/{url}', timeout=None)

    if resp.status_code in (429, 403):  # Too Many Requests
        raise PossibleIPBlockError

    if resp.status_code == 302:
        # The work is being checked by a teacher. Ignore.
        return None

    if resp.status_code != 200:
        with open('error.html.bak', 'w', encoding=resp.encoding) as logf:
            logf.write(resp.text)

        raise PyaklassError(
            f'Ошибка ({resp.status_code}) при выполнении запроса {BASE_URL}/{url}.',
        )

    if 'SolveCaptcha' in resp.url.path:
        return await solve_captcha(client, limiter, resp.url.params)
    return resp.text


async def fetch_and_parse(client, limiter: tuple, url: str):
    """Получить и спарсить HTML-страницу.

    Args:
        client (httpx.AsyncClient): Клиент
        limiter (tuple): Ограничитель и его синхронизатор
        url (str): Путь для следующего URL: `https://www.yaklass.ru/{url}`

    Returns:
        Union[LexborHTMLParser, None]: Парсер или None в случае 309 (Работа еще проверяется)
    """
    text = await fetch(client, limiter, url)
    return LexborHTMLParser(text) if text else None
