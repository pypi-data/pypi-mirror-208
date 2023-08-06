"""Парсинг результатов прошедшей работы."""


def _open_text_chunk(element) -> dict:
    if element.child and element.child.tag != '-text':
        text_chunk = _open_text_chunk(element.child)
    else:
        text_chunk = {'styles': [], 'text': element.html}

    if element.tag == 'strong':
        text_chunk['styles'].append('bold')
    if element.tag in {'em', 'i'}:
        text_chunk['styles'].append('italic')

    return text_chunk


def _fix_text(element) -> list:
    return [_open_text_chunk(el) for el in element.iter(include_text=True)]


def _parse_warning(element) -> dict:
    return {
        'type': 'warning',
        'title': element.css_first('.gxst-ititle > span').text(deep=False),
        'text': _fix_text(element.css_first('.gxst-ibody')),
    }


def _parse_image(element) -> dict:
    return {'type': 'image', 'src': element.css_first('.gxs-resource-image').attrs['src']}


def _parse_file_link(element) -> dict:
    # NOTE: This is not a typo.
    # For sharing similar field names between objects 'href' is named as 'src'.
    return {'type': 'file', 'src': element.css_first('.gxs-resource-file').attrs['href']}


def _parse_table(element) -> dict:
    table = element.css_first('table')

    rows = []
    current_tr = None
    for td_el in table.css('td'):
        data = [
            *(_fix_text(el) for el in td_el.iter(include_text=True) if el.tag != 'br'),
            ['\n'],
        ]

        if current_tr == td_el.parent:
            rows[-1].append(data)
        else:
            current_tr = td_el.parent
            rows.append(data)

    return {
        'type': 'table',
        'rows': rows,
    }


def parse_work_results(results: list, exercise_page):
    """Спарсить результаты прошедшей работы.

    Args:
        results (list): Результаты
        exercise_page (LexborHTMLParser): HTML-страница с заданием
    """
    title = exercise_page.css_first('.type-name').text(deep=False)

    score_el = exercise_page.css_first('.bottom-buffer-1')
    score = int(score_el.css_first('#earned-points-val').text(deep=False))
    max_score = int(score_el.text(deep=False, strip=True)[3:])

    results.append({
        'title': title,
        'body': tuple(el.html for el in exercise_page.css('#taskhtml > div > div')),
        'score': score,
        'max_score': max_score,
    })
