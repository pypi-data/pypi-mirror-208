from google_sheets_telegram_utils.utils.configs.abstract_config import AbstractConfig


class CsvConfig(AbstractConfig):
    def __init__(self, file):
        self.file = file
