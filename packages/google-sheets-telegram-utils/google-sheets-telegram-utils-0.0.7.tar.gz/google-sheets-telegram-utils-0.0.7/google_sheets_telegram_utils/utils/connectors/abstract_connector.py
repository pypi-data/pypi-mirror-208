from abc import ABC, abstractmethod

from google_sheets_telegram_utils.utils.configs.abstract_config import AbstractConfig


class AbstractConnector(ABC):
    def __init__(self, config: AbstractConfig):
        pass

    @abstractmethod
    async def get_data(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def add_rows(self, rows: list) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_row(self, row):
        raise NotImplementedError

    @abstractmethod
    async def get_row_by_id(self, pk) -> dict:
        raise NotImplementedError
