from google_sheets_telegram_utils.utils.configs.abstract_config import AbstractConfig


class GoogleSheetConfig(AbstractConfig):
    def __init__(self, credentials_path, scope, file, sheet_name):
        self.credentials_path = credentials_path
        self.scope = scope
        self.file = file
        self.sheet_name = sheet_name
