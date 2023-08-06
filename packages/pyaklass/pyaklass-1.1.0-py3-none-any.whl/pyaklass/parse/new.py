"""Парсинг активных работ."""
from pyaklass.const import BASE_URL
from pyaklass.parse.func import fetch_and_parse


def parse_new_works(testworks: list, elements: list):
    """Спарсить информацию о новых работах.

    Args:
        testworks (list): Список, в который добавляются работы
        elements (list): Список `<table>`-элементов
    """
    for elem in elements:
        link_elem = elem.css_first('a')

        href = link_elem.attrs['href']
        test_id = int(href[href.rindex('/') + 1:])

        deadline_unix = int(elem.css_first('[data-utc-date]').attrs['data-utc-date'][:-3])
        subject = elem.css_first('.subject').text(deep=False, strip=True)

        testworks.append({
            'id': test_id,
            'title': link_elem.text(deep=False),
            'subject': subject,
            'deadline_unix': deadline_unix,
        })


def parse_new_work_details(testwork: dict, testwork_page):
    """Спарсить дополнительные сведения о новой работе.

    Args:
        testwork (dict): Работа
        testwork_page (LexborHTMLParser): HTML-страница со сведениями
    """
    blockbody_el = testwork_page.css_first('.blockbody')

    max_attempts = int(blockbody_el.css_first('p:last-of-type > .value').text(deep=False))
    themes = [
        (
            f"{BASE_URL}{theme_el.attrs['href']}",
            theme_el.text(deep=False),
        ) for theme_el in blockbody_el.css('.test-work-used-topics a')
    ]

    testwork.update({
        'max_attempts': max_attempts,
        'themes': themes,
    })


async def fetch_and_parse_new_work_details(client, limiter: tuple, testwork: dict):
    """Получить и парсить дополнительные сведения о новой работе.

    Args:
        client (AsyncClient): Клиент
        limiter (tuple): Ограничитель и его синхронизатор
        testwork (dict): Работа

    Returns:
        dict: Работа
    """
    testwork_page = await fetch_and_parse(
        client, limiter, f"TestWorkRun/Preview/{testwork['id']}",
    )
    parse_new_work_details(testwork, testwork_page)
    return testwork
