import requests
from requests import Response


class TelegramHandler:

    def __init__(self, token: str):
        """
        :param token: Telegram token
        """
        self.token: str = ''
        self.configure(token)

    def __init__(self):
        self.token: str = ''

    def configure(self, token: str) -> None:
        """
        Configurator
        :param token: Telegram token
        :return: None
        """
        self.token = token

    def send_message(self, chat_id: int, text: str) -> Response:
        """
        Send telegram message
        Telegram token must be configured before sending message.
        :param chat_id: Telegram chat id
        :param text: message to send
        :return: Response object in requests HTTP library
        """
        url_req = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}'
        return requests.get(url_req)
