"""Аккаунт."""
from httpx import AsyncClient

from pyaklass import parse
from pyaklass.const import BASE_URL
from pyaklass.exc import LoginError, PyaklassError
from pyaklass.testworks import get_results, get_testworks


class Account:
    """Аккаунт."""

    def __init__(self, login: str, password: str, manager=None):
        """Инициализировать аккаунт.

        Args:
            login (str): Логин
            password (str): Пароль
            manager (Union[multiprocessing.managers.SyncManager, None]): Менеджер процессов.

        `manager` может быть `None` для установки параметров вручную или через `AccountManager`.
        """
        self.__login = login
        self.__password = password

        # self.limiter[1] is a special dict for containing information about rate limits.
        if manager:
            lock = manager.Lock()
            self.limiter = (
                lock,
                manager.Value(dict, {'amount': 28, 'seconds': 10, 'current': 0}, lock),
            )
        else:
            self.limiter = (None, None)

        self.__is_logged_in = False
        self.client = AsyncClient(headers={
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Google Chrome";v="108", "Chromium";v="108", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            ),
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-HTTPS': '1',
        }, follow_redirects=True)

    def get_login(self) -> str:
        """Вернуть логин.

        Returns:
            str: Логин
        """
        return self.__login

    def set_login(self, value: str):
        """Изменить логин для входа.

        Args:
            value (str): Новое значение
        """
        self.__login = value

    def set_password(self, value: str):
        """Изменить пароль для входа.

        Args:
            value (str): Новое значение
        """
        self.__password = value

    async def login(self):
        """Вход в аккаунт.

        Raises:
            LoginError: Ошибка входа в аккаунт
            ValueError: Вход в аккаунт уже был произведен
            TypeError: Пароль или логин пуст / Менеджер процессов не был указан при инициализации
        """
        if self.__is_logged_in:
            raise ValueError('Вход в аккаунт уже был произведен.')
        if not self.__login or not self.__password:
            raise TypeError('Логин или пароль пуст.')
        if not any(self.limiter):
            raise TypeError((
                'Менеджер процессов не был указан при инициализации. '
                'Для ручного создания ограничителя переопределите его значение.'
            ))

        try:
            login_page = await parse.func.fetch_and_parse(
                self.client, self.limiter, 'Account/Login',
            )
        except PyaklassError as exc:
            raise LoginError(exc.message) from exc

        crsf_token = login_page.css_first('#PostToken').attrs['value']
        payload = {
            'UserName': self.__login,
            'Password': self.__password,
            'RememberMe': 'true',
            'ReturnUrl': '',
            'AuthAction': 'lor',  # Login Or Register
            'RedirectReason': '',
            'PostToken': crsf_token,
        }
        await parse.func.check_limiter(*self.limiter)
        resp = await self.client.post(f'{BASE_URL}/Account/Login', data=payload)
        if resp.url.path == '/Account/Login':
            raise LoginError('Неправильный логин или пароль.')

        self.__password = ''  # noqa: S105
        self.__is_logged_in = True

    async def get_new_testworks(self) -> list:
        """Получить список активных работ.

        Returns:
            list: Работы
        """
        return await get_testworks(self.client, self.limiter, remove_old=True)

    async def get_all_testworks(self) -> list:
        """Получить список всех работ.

        Returns:
            list: Работы
        """
        return await get_testworks(self.client, *self.limiter)

    async def get_results(self, testwork_id: int, result_id: int) -> list:
        """Получить результаты прошедшей работы.

        Args:
            testwork_id (int): ID прошедшей работы
            result_id (int): ID результатов для работы

        Returns:
            list: Результаты
        """
        return await get_results(self.client, self.limiter, testwork_id, result_id)

    def __str__(self) -> str:
        """Вернуть удобно-читаемое представление объекта.

        Returns:
            str: Логин
        """
        return f'Аккаунт {self.__login}'
