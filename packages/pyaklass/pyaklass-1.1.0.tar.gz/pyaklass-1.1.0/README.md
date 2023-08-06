# PYaKlass

Быстрый асинхронный модуль для работы с ЯКлассом.

**Функции:**

* Обход капчи
* Получение активных работ
* Получение всех работ (На данный момент только первой страницы)

## Примеры

### Получение активных работ
```python
from multiprocessing.managers import SyncManager

from pyaklass import Account

# Иначе: manager.start() и manager.shutdown()
with SyncManager() as manager:
    account = Account('login', 'password', manager)
    await account.login()

    testworks = await account.get_new_testworks()  # -> List[dict[str, Any]]
    print(testworks)
```

### Работа с несколькими аккаунтами
```python
from pyaklass import Account
from pyaklass.manager import AccountManager

# Здесь не требуется указывать SyncManager, так как AccountManager создает его сам.
# При различных менеджерах есть шанс блокировки вашего IP сервисом!
manager = AccountManager(
    Account('login1', 'password1'),
    Account('login2', 'password2'),
    Account('login3', 'password3'),
)
if not any(await manager.prepare()):
    print('Не получилось войти ни в один аккаунт.')

testworks_per_account = await manager.get_new_testworks()  # -> List[List[dict]]
print(testworks)
```

### Получение результатов прошедших работ

> **Примечание:**
> Пользователь может получить только свои результаты.

```python
from multiprocessing.managers import SyncManager

from pyaklass import Account

# Иначе: manager.start() и manager.shutdown()
with SyncManager() as manager:
    account = Account('login', 'password', manager)
    await account.login()

    results = await account.get_results(testwork_id=..., result_id=...)
    print(results)
```

## TODO

Будет сделано при желании и возможности.

- [ ] Брутфорс тестовых заданий
- [ ] Парсинг результатов, времени прохождения, введенных ответов
- [ ] Парсинг ФИО учителя, задавшего работу
- [ ] Использовать API пагинации вместо парсинга списка работ
  - [ ] `https://www.yaklass.ru/ajax/TestWork/GetStudentTestWorksAjax?type=FinishedTestWorks&page=1&from=%2FTestWork`
