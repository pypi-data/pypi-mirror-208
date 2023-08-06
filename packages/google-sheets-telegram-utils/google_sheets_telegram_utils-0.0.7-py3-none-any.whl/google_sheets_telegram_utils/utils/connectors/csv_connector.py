import os
import csv
from google_sheets_telegram_utils.utils.configs.csv_config import CsvConfig
from google_sheets_telegram_utils.utils.connectors.abstract_connector import AbstractConnector


class CsvConnector(AbstractConnector):

    def __init__(self, config: CsvConfig):
        super().__init__(config)
        self.config = config

    def init_file(self):
        if not os.path.exists(self.config.file):
            with open(self.config.file, 'w'):
                ...

    async def get_data(self) -> csv.DictReader:
        with open(self.config.file) as csv_file:
            data = csv.DictReader(csv_file)
        return data

    async def _read_fields_and_rows(self) -> list:
        rows = []
        with open(self.config.file) as csv_file:
            csvreader = csv.reader(csv_file)
            for row in csvreader:
                rows.append(row)
        return rows

    async def _get_last_id(self) -> int:
        data = await self._read_fields_and_rows()
        if not data:
            return 0
        return int(data[-1][0])

    async def add_rows(self, rows: list) -> None:
        new_id = await self._get_last_id() + 1
        with open(self.config.file, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in rows:
                row.insert(0, new_id)
                csv_writer.writerow(row)

    async def add_row(self, row) -> None:
        await self.add_rows([row])

    async def get_row_by_id(self, pk) -> dict:
        data = await self._read_fields_and_rows()
        filtered_data = list(filter(lambda row: row[0] == pk, data))
        return filtered_data[0]
