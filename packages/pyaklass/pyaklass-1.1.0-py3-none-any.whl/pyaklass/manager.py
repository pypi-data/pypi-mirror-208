"""Менеджер для работы с несколькими аккаунтами одновременно."""
import asyncio
from functools import partial
from multiprocessing import Pool
from multiprocessing.managers import SyncManager

from httpx import AsyncClient
from selectolax.lexbor import LexborHTMLParser

from pyaklass import Account
from pyaklass.exc import LoginError
from pyaklass.parse.func import fetch
from pyaklass.testworks import get_testworks


def _w_get_new_testworks(args, limiter: tuple) -> list:
    client = AsyncClient(headers=args[0]['headers'], cookies=args[0]['cookies'])
    testwork_page = LexborHTMLParser(args[1])

    loop = asyncio.new_event_loop()
    return loop.run_until_complete(
        get_testworks(client, limiter, testwork_page, remove_old=True),
    )


def _w_get_all_testworks(args, limiter: tuple):
    client = AsyncClient(headers=args[0]['headers'], cookies=args[0]['cookies'])
    testwork_page = LexborHTMLParser(args[1])

    loop = asyncio.new_event_loop()
    return loop.run_until_complete(get_testworks(client, limiter, testwork_page))


class AccountManager:
    """Менеджер для работы с несколькими аккаунтами одновременно."""

    def __init__(self, *accounts: Account, procs: int = None):
        """Инициализировать менеджер аккаунтов.

        Args:
            accounts (tuple[Account]): Аккаунты, в которые не вошли
            procs (int): Количество процессов для параллельного парсинга
        """
        self.accounts = list(accounts)
        self.procs = procs

        # An account manager will create a global SyncManager for managing shared objects.
        self._manager = SyncManager()
        self.limiter = None

    async def prepare(self) -> list:
        """Подготовить аккаунты.

        Returns:
            list: Результат (`bool`) входа в аккаунты
        """
        self._manager.start()  # pylint: disable=consider-using-with

        lock = self._manager.Lock()
        self.limiter = (
            lock,
            self._manager.Value(dict, {'amount': 28, 'seconds': 10, 'current': 0}, lock),
        )

        async def login_or_pop(account):
            account.limiter = self.limiter

            try:
                await account.login()
                return True
            except LoginError:
                self.accounts.remove(account)
                return False

        return await asyncio.gather(*(login_or_pop(account) for account in self.accounts))

    async def _get_testworks(self, pool_func) -> list:
        with Pool(processes=self.procs) as pool:
            # NOTE: We obtain pages here instead of doing it in account.get_active_testworks(),
            # because parsing is a synchronous operation and asyncio.gather cannot perform it
            # in parallel.
            testwork_pages = await asyncio.gather(*(
                fetch(acc.client, self.limiter, '/testwork?from=menu') for acc in self.accounts
            ))
            return pool.map(
                partial(pool_func, limiter=self.limiter),
                zip(
                    [{
                        'headers': dict(account.client.headers),
                        'cookies': dict(account.client.cookies),
                    } for account in self.accounts],
                    testwork_pages,
                ),
            )

    async def get_new_testworks(self) -> list:
        """Получить список активных работ.

        Returns:
            list: Список работ для каждого аккаунта
        """
        return await self._get_testworks(_w_get_new_testworks)

    async def get_all_testworks(self) -> list:
        """Получить список всех работ.

        Returns:
            list: Список работ для каждого аккаунта
        """
        return await self._get_testworks(_w_get_all_testworks)

    def release(self):
        """Освободить ресурсы, занятые обьектами менеджера."""
        self._manager.shutdown()

    def __str__(self) -> str:
        """Вернуть удобно-читаемое представление объекта.

        Returns:
            str: Краткая информация
        """
        return f'Менеджер, работающий с {len(self.accounts)} аккаунтами'
