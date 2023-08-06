import telebot


class zui_bot(telebot.TeleBot):
    def __init__(self, token: str):
        super().__init__(token)

    def send_file(self, chat_id: int | str, file_path: str):
        with open(file_path, "rb") as f:
            super().send_document(chat_id, f)


def create_bot(token: str):
    '''
    Detail API: https://pypi.org/project/pyTelegramBotAPI
    '''
    # return telebot.TeleBot(token)
    return zui_bot(token)
