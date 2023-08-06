"""Внутренние функции для получения информации о работах."""
from asyncio import gather
from time import time

from pyaklass import parse


async def get_testworks(client, limiter: tuple, testworks_page=None, remove_old=False) -> list:
    """Получить работы.

    Args:
        client (httpx.AsyncClient): Авторизированный клиент
        limiter (tuple): Ограничитель и его синхронизатор
        testworks_page (LexbotHTMLParser): HTML-страница с работами
        remove_old (bool): Игнорировать работы, заданные больше 30 дней назад?

    Returns:
        list: Работы
    """
    testworks = []

    if not testworks_page:
        testworks_page = await parse.func.fetch_and_parse(
            client, limiter, '/testwork?from=menu',
        )
    new_works_el, completed_works_el = testworks_page.css('.wg-testworks')

    if not new_works_el.css_first('.wg-empty'):
        parse.new.parse_new_works(testworks, new_works_el.css('table'))
        testworks = await gather(*(
            parse.new.fetch_and_parse_new_work_details(
                client, limiter, tw,
            ) for tw in testworks
        ))

    if not completed_works_el.css_first('.wg-empty'):
        completed_testworks = []
        parse.completed.parse_completed_works(
            completed_testworks, completed_works_el.css('tbody > tr'),
        )

        if remove_old:
            completed_testworks = tuple(filter(
                lambda tw: (time() - tw.pop('submit_unix')) <= 2592000,
                completed_testworks,
            ))

        completed_testworks = await gather(*(
            parse.completed.fetch_and_parse_completed_work_details(
                client, limiter, tw,
            ) for tw in completed_testworks
        ))
        testworks.extend(filter(lambda tw: tw, completed_testworks))

    return testworks


async def get_results(
    client, limiter: tuple, testwork_id: int, result_id: int, pages: list = None,
) -> list:
    """Получить результаты прошедшей работы.

    Args:
        client (httpx.AsyncClient): Авторизированный клиент
        limiter (tuple): Ограничитель и его синхронизатор
        testwork_id (int): ID прошедшей работы
        result_id (int): ID результатов для работы
        pages (list): HTML-страницы для парсинга

    Returns:
        list: Результаты
    """
    results = []

    if not pages:
        exercises_list_page = await parse.func.fetch_and_parse(
            client,
            limiter,
            f'TestWork/Results/{testwork_id}?from=%2FTestWork',
        )
        exercises_pos = int(
            exercises_list_page.css('.adjust')[-1].text(deep=False, strip=True),
        )

        pages = await gather(*(
            parse.func.fetch_and_parse(
                client,
                limiter,
                (
                    f'TestWork/ExerciseResult?testResultId={result_id}'
                    f'&exercisePosition={pos}&twId={testwork_id}'
                ),
            ) for pos in range(1, exercises_pos + 1)
        ))

    for exercise_page in pages:
        parse.results.parse_work_results(results, exercise_page)

    return results
