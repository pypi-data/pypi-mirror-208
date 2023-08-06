import telegram


class TelegramUser:
    def __init__(self, data: dict):
        #  TODO move id, username... to constants
        self.id = data['id']
        self.username = data['username']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.language_code = data['language_code']
        self.is_bot = data['is_bot']
        self.is_activated = data.get('is_activated', '').lower() == 'true'

    @classmethod
    def from_telegram_user(cls, telegram_user: telegram._user.User) -> 'TelegramUser':
        data = {
            'id': telegram_user.id,
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name,
            'language_code': telegram_user.language_code,
            'is_bot': telegram_user.is_bot,
        }
        return cls(data)

    def convert_to_list(self) -> list:
        return [
            self.id,
            self.username,
            self.first_name,
            self.last_name,
            self.language_code,
            self.is_bot,
            'TRUE' if self.is_activated else 'FALSE',
        ]
