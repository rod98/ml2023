import requests
import json

class SimpleTelegramApi:
    def __init__(self, api_token):
        self.api_token = api_token

    def setup_webhook(self, url):
        telegram_webhook_url = f"https://api.telegram.org/bot{self.api_token}/setWebhook?url={url}"
        requests.get(telegram_webhook_url)

    def send_message(self, chat_id, text):
        url = f'https://api.telegram.org/bot{self.api_token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'html'
        }

        r = requests.post(url, json=payload).json()

        return r

    def edit_message(self, chat_id, msg_id, text):
        url = f"https://api.telegram.org/bot{self.api_token}/editMessageText" #?chat_id={chat_id}&message_id={msg_id}"
        payload = {
            'chat_id': chat_id,
            'message_id': msg_id,
            'text': text
        }
        r = requests.post(url, json=payload).json()
        return r

    def delete_message(self, chat_id, msg_id):
        url = f"https://api.telegram.org/bot{self.api_token}/deleteMessage?chat_id={chat_id}&message_id={msg_id}"
        r = requests.post(url).json()
        return r
