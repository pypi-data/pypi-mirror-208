class BotException(Exception):
    def __init__(self, message='BotException'):
        super().__init__(message)


class RowDoesNotExistException(BotException):
    def __init__(self, message='Row does not exist'):
        super().__init__(message)
