"""Исключения для PYaKlass."""


class PyaklassError(Exception):
    """Базовый класс для исключений."""

    def __init__(self, reason: str):
        """Инициализировать исключение.

        Args:
            reason (str): Причина
        """
        self.message = reason

    def __str__(self) -> str:
        """Вернуть удобно-читаемое представление исключения.

        Returns:
            str: Сообщение исключения
        """
        return self.message


class LoginError(PyaklassError):
    """Ошибка входа."""


class PossibleIPBlockError(PyaklassError):
    """Ошибка из-за возможной блокировки IP сервисом."""

    def __init__(self):
        """Инициализировать исключение."""
        super().__init__('Инициализировано исключение для предотвращения блокировки IP сервисом.')
