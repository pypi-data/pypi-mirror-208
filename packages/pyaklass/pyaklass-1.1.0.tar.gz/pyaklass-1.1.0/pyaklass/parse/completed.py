"""Парсинг прошедших работ."""
from time import time

from pyaklass.parse.func import fetch_and_parse


def parse_completed_works(testworks: list, elements: list):
    """Спарсить информацию о прошедших работах.

    Args:
        testworks (list): Список, в который добавляются работы
        elements (list): Список `<tr>`-элементов
    """
    for elem in elements:
        link_elem = elem.css_first('a')

        href = link_elem.attrs['href']
        test_id = int(href[href.rindex('/') + 1:href.rfind('?')])

        submit_unix = int(elem.css_first('[data-utc-date]').attrs['data-utc-date'][:-3])
        subject = elem.css_first('.subject').text(deep=False, strip=True)

        testworks.append({
            'id': test_id,
            'title': link_elem.text(deep=False, strip=True),
            'subject': subject,
            'submit_unix': submit_unix,
        })


def parse_completed_work_details(testwork: dict, testwork_page) -> bool:
    """Спарсить дополнительные сведения о прошедшей работе.

    Args:
        testwork (dict): Работа
        testwork_page (LexborHTMLParser): HTML-страница со сведениями

    Returns:
        bool: Доступна ли работа для сдачи в данный момент?
    """
    info_el = testwork_page.css_first('#testwork')
    if not info_el:
        return False

    script_text: str = testwork_page.css_first('body > script:last-of-type').text(deep=False)

    deadline_unix = script_text[script_text.index('endUTC:') + 7:]
    deadline_unix = float(deadline_unix[:deadline_unix.index(',')]) / 1000

    max_attempts = script_text[script_text.index('triesAllowed:"') + 14:]
    max_attempts = int(max_attempts[:max_attempts.index('"')])

    results_el = testwork_page.css_first('.data-row')
    if results_el.css_first('.data-content > em'):  # The work has been skipped
        results_id = None
        exercises = int(testwork_page.css('.adjust')[-1].text(deep=False))
    else:
        results_id = int(results_el.attrs['data-test-result-id'])
        exercises = int(testwork_page.css('[data-ex-pos]')[-1].attrs['data-ex-pos'])

    testwork.update({
        'deadline_unix': deadline_unix,
        'max_attempts': max_attempts,
        'results_id': results_id,
        'exercises': exercises,
    })
    return (time() - deadline_unix) >= 1


async def fetch_and_parse_completed_work_details(client, limiter, testwork: dict):
    """Получить и парсить дополнительные сведения о прошедшей работе.

    Args:
        client (AsyncClient): Клиент
        limiter (tuple): Ограничитель и его синхронизатор
        testwork (dict): Работа

    Returns:
        Union[dict, None]: Работа или None в случае, если работа недоступна для сдачи
    """
    testwork_page = await fetch_and_parse(
        client, limiter, f"TestWork/Results/{testwork['id']}?from=%2Ftestwork",
    )
    if testwork_page and parse_completed_work_details(testwork, testwork_page):
        return testwork
